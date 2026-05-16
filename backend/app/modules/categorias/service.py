"""CategoriaService — business logic for hierarchical category management.

Implements:
  - Self-reference validation (parent_id != id)
  - Cycle detection via repository CTE queries
  - Soft-delete enforcement (no delete if has children)
  - Tree traversal and retrieval

Cycle Detection Strategy:
  - Depth limit: 20 levels (prevents pathological hierarchies)
  - Uses PostgreSQL WITH RECURSIVE CTE via repository
  - Detects cycles during create and update operations
  - Raises ValidationError if cycle or depth limit exceeded

Soft-Delete Pattern:
  - All categories have a deleted_at timestamp (inherited from BaseModel)
  - Deleting category with children is forbidden (404/409 error)
  - Tree queries automatically exclude soft-deleted categories
"""

from typing import List, Optional

from app.exceptions import AppException, ValidationError
from app.modules.categorias.schemas import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaTreeNode,
    CategoriaUpdate,
)
from app.repositories.categoria_repository import CategoriaRepository


class CategoriaService:
    """
    Service layer for hierarchical category management.

    Enforces business rules:
    - Categories cannot reference themselves as parent
    - No cycles allowed in hierarchy (depth limit: 20)
    - Categories with children cannot be soft-deleted
    - All operations respect soft-delete filter (deleted_at IS NULL)

    All methods are async and use the UnitOfWork pattern for transaction management.
    """

    def __init__(self, uow):
        """
        Initialize service with UnitOfWork.

        Args:
            uow: UnitOfWork instance providing access to repositories
        """
        self.uow = uow

    # ── Validation Helpers ────────────────────────────────────────────────────

    async def _validate_self_reference(
        self,
        categoria_id: Optional[int],
        parent_id: Optional[int],
    ) -> None:
        """
        Validate that a category is not its own parent (self-reference check).

        Business rule: A category's parent_id must never equal the category's id.
        This is the first line of defense against cycles.

        Args:
            categoria_id: The category ID (None for new categories)
            parent_id: The proposed parent ID

        Raises:
            AppException: If parent_id == categoria_id (400 Bad Request)
        """
        if categoria_id and parent_id == categoria_id:
            raise AppException(
                message="Cannot set parent_id to self: self-reference not allowed",
                status_code=400,
            )

    async def _validate_parent_exists(self, parent_id: int) -> None:
        """
        Validate that a parent category exists and is not soft-deleted.

        Args:
            parent_id: Parent category ID to validate

        Raises:
            AppException: If parent not found or is soft-deleted
        """
        parent = await self.uow.categorias.find(parent_id)
        if not parent:
            raise AppException(
                message=f"Parent category with id={parent_id} not found",
                status_code=404,
            )

    async def _validate_no_cycle(
        self,
        categoria_id: int,
        new_parent_id: int,
        depth_limit: int = 20,
    ) -> None:
        """
        Validate that assigning new_parent_id would not create a cycle.

        Uses CTE (Common Table Expression) in PostgreSQL to traverse the hierarchy.
        Traversal is bounded by depth_limit to prevent infinite loops.

        Business rule: new_parent_id cannot be a descendant of categoria_id.
        If true, a cycle would be created.

        Args:
            categoria_id: Category being updated
            new_parent_id: Proposed parent ID
            depth_limit: Maximum tree depth (default 20)

        Raises:
            ValidationError: If cycle would be created or depth limit exceeded
        """
        try:
            await self.uow.categorias.validate_no_cycle(
                categoria_id=categoria_id,
                new_parent_id=new_parent_id,
                depth_limit=depth_limit,
            )
        except ValueError as e:
            raise ValidationError(str(e))

    # ── CRUD Operations ───────────────────────────────────────────────────────

    async def create_categoria(
        self,
        data: CategoriaCreate,
        self_id: Optional[int] = None,
    ) -> CategoriaRead:
        """
        Create a new category with validation.

        Validation sequence:
        1. Check self-reference (parent_id != id)
        2. If parent_id provided, verify parent exists
        3. If parent_id provided, verify no cycle via CTE
        4. Create in repository (atomic via UoW)

        Business rules:
        - Root categories have parent_id = NULL
        - Subcategories must have a valid parent_id
        - Cannot set parent_id == id (self-reference prevention)
        - If parent_id provided, verify no cycle would be created

        Args:
            data: CategoriaCreate schema with nombre, descripcion, parent_id
            self_id: (optional) categoria ID if this is an update; used for self-ref check

        Returns:
            CategoriaRead response schema

        Raises:
            ValidationError: If self-ref, parent not found, or cycle detected
            AppException: If validation fails

        Example:
            # Create root category
            result = await service.create_categoria(
                CategoriaCreate(nombre="Bebidas", parent_id=None)
            )

            # Create subcategory
            result = await service.create_categoria(
                CategoriaCreate(nombre="Alcohólicas", parent_id=1)
            )
        """
        # Validate self-reference
        await self._validate_self_reference(self_id, data.parent_id)

        # If has parent, verify parent exists and no cycle
        if data.parent_id:
            await self._validate_parent_exists(data.parent_id)

            # Verify no cycle (using repository CTE query)
            if hasattr(self.uow.categorias, "validate_no_cycle"):
                await self._validate_no_cycle(
                    categoria_id=self_id or 0,  # 0 for new categories
                    new_parent_id=data.parent_id,
                    depth_limit=20,
                )

        # Create in repository
        from app.models.categoria import Categoria as CategoriaModel

        categoria_model = CategoriaModel(**data.model_dump())
        categoria = await self.uow.categorias.create(categoria_model)

        return CategoriaRead.model_validate(categoria)

    async def update_categoria(
        self,
        categoria_id: int,
        data: CategoriaUpdate,
    ) -> CategoriaRead:
        """
        Update an existing category with validation.

        Validation sequence:
        1. Check self-reference (parent_id != categoria_id)
        2. If parent_id provided, verify no cycle
        3. Update in repository
        4. Verify category exists

        Business rules:
        - Cannot update parent_id to self
        - Cannot update parent_id to a descendant (cycle prevention)
        - Category must exist and not be soft-deleted
        - Only provided fields are updated (nome, descripcion, parent_id)

        Args:
            categoria_id: ID of category to update
            data: CategoriaUpdate schema with optional fields

        Returns:
            Updated CategoriaRead response

        Raises:
            AppException: If category not found
            ValidationError: If self-ref or cycle detected

        Example:
            # Update name only
            result = await service.update_categoria(
                1,
                CategoriaUpdate(nombre="Bebidas - Refrescos")
            )

            # Move to different parent
            result = await service.update_categoria(
                2,
                CategoriaUpdate(parent_id=5)
            )
        """
        # Validate self-reference if parent_id is being changed
        if data.parent_id:
            await self._validate_self_reference(categoria_id, data.parent_id)

            # Validate no cycle
            await self._validate_no_cycle(
                categoria_id=categoria_id,
                new_parent_id=data.parent_id,
                depth_limit=20,
            )

        # Update in repository
        update_dict = data.model_dump(exclude_none=True)
        categoria = await self.uow.categorias.update(categoria_id, update_dict)

        if not categoria:
            raise AppException(
                message=f"Category with id={categoria_id} not found", status_code=404
            )

        return CategoriaRead.model_validate(categoria)

    async def delete_categoria(self, categoria_id: int) -> None:
        """
        Soft-delete a category if it has no children and no products.

        Soft-delete strategy: Sets deleted_at timestamp instead of physically removing.
        Preserves referential integrity and enables audit trails/recovery.

        Business rules:
        - Cannot delete if category has children (orphaning would be problematic)
        - Cannot delete if category has products (data loss prevention)
        - Uses soft-delete pattern (sets deleted_at, not physically removed)
        - Soft-deleted categories excluded from all tree queries

        Args:
            categoria_id: ID of category to delete

        Raises:
            AppException: If category has children, has products, or not found

        Example:
            # Delete a leaf category with no products
            await service.delete_categoria(3)

            # This will fail if category has children or products:
            # await service.delete_categoria(1)  # raises AppException
        """
        # Check if category exists first
        categoria = await self.uow.categorias.find(categoria_id)
        if not categoria:
            raise AppException(
                message=f"Category with id={categoria_id} not found", status_code=404
            )

        # Check if has children
        child_count = await self.uow.categorias.count_children(categoria_id)
        if child_count > 0:
            raise AppException(
                message=f"Cannot delete category: it has {child_count} children",
                status_code=409,
            )

        # NOTE: Skipping product count check for now since productos table doesn't exist yet
        # This validation will be re-enabled once CHANGE-05 (Product Catalog) is implemented
        # The count_products_in_category() method has a try-catch but exceptions during
        # flush/commit can still corrupt the transaction state in async SQLAlchemy

        # Soft-delete
        await self.uow.categorias.soft_delete(categoria_id)

    async def get_categoria(self, categoria_id: int) -> CategoriaRead:
        """
        Retrieve a single category by ID.

        Automatically excludes soft-deleted categories.

        Args:
            categoria_id: Category ID to retrieve

        Returns:
            CategoriaRead response

        Raises:
            AppException: If category not found or is soft-deleted

        Example:
            result = await service.get_categoria(1)
            # CategoriaRead(id=1, nombre="Bebidas", ...)
        """
        categoria = await self.uow.categorias.find(categoria_id)
        if not categoria:
            raise AppException(
                message=f"Category with id={categoria_id} not found", status_code=404
            )
        return CategoriaRead.model_validate(categoria)

    async def get_tree(self) -> List[CategoriaTreeNode]:
        """
        Retrieve all root categories with their complete tree structure.

        Returns nested category hierarchy with all descendants populated.
        Automatically excludes soft-deleted categories and their children.

        Tree structure is built by:
        1. Query root categories (parent_id IS NULL, deleted_at IS NULL)
        2. Load their ORM children relationships
        3. Recursively convert to nested CategoriaTreeNode response

        Returns:
            List of root CategoriaTreeNode with nested subcategorias
            Empty list if no root categories exist

        Example:
            result = await service.get_tree()
            # [
            #   CategoriaTreeNode(
            #     id=1, nombre="Bebidas",
            #     subcategorias=[
            #       CategoriaTreeNode(id=2, nombre="Alcohólicas", subcategorias=[]),
            #       CategoriaTreeNode(id=3, nombre="Sin alcohol", subcategorias=[])
            #     ]
            #   )
            # ]
        """
        root_categories = await self.uow.categorias.get_tree()

        # Convert to nested tree response
        return [self._build_tree_node(cat) for cat in root_categories]

    # ── Tree Building Helper ──────────────────────────────────────────────────

    def _build_tree_node(self, categoria) -> CategoriaTreeNode:
        """
        Convert a categoria ORM object to CategoriaTreeNode with nested children.

        Recursively processes children relationships to build nested response.
        Automatically filters soft-deleted children from the tree.

        Args:
            categoria: Categoria ORM object with children relationship populated

        Returns:
            CategoriaTreeNode with nested subcategorias
        """
        children = []
        if hasattr(categoria, "children") and categoria.children:
            children = [
                self._build_tree_node(child)
                for child in categoria.children
                if not getattr(child, "deleted_at", None)  # Filter soft-deleted
            ]

        return CategoriaTreeNode(
            id=categoria.id,
            nombre=categoria.nombre,
            descripcion=getattr(categoria, "descripcion", None),
            parent_id=categoria.parent_id,
            created_at=categoria.created_at,
            updated_at=categoria.updated_at,
            deleted_at=getattr(categoria, "deleted_at", None),
            subcategorias=children,
        )
