"""CategoriaRepository — repository for hierarchical categories with CTE support"""
import logging
from typing import List, Optional
from sqlalchemy import select, func, text, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categoria import Categoria
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CategoriaRepository(BaseRepository[Categoria]):
    """
    Repository for categories with hierarchical query support.
    
    Provides specialized methods for:
    - Recursive CTE queries for tree traversal
    - Cycle detection on parent assignments
    - Child/descendant counting for validation
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository
        
        Args:
            session: AsyncSession instance
        """
        super().__init__(session, Categoria)
    
    async def get_tree(self, depth_limit: int = 20) -> List[Categoria]:
        """
        Fetch all root categories (parent_id IS NULL) with their complete tree.
        
        Uses PostgreSQL WITH RECURSIVE CTE to fetch the entire hierarchical tree
        in a single query, then reconstructs relationships in-memory via ORM.
        
        Args:
            depth_limit: Maximum tree depth (prevents infinite recursion)
            
        Returns:
            List of root Categoria objects with children populated
        """
        # Use CTE to fetch entire tree structure (all non-deleted categories)
        query = text("""
            WITH RECURSIVE category_tree AS (
                -- Anchor: root categories (parent_id IS NULL)
                SELECT id, nombre, descripcion, parent_id, created_at, updated_at, deleted_at, 1 as depth
                FROM categorias
                WHERE parent_id IS NULL AND deleted_at IS NULL
                
                UNION ALL
                
                -- Recursive: children of categories already in tree
                SELECT c.id, c.nombre, c.descripcion, c.parent_id, c.created_at, c.updated_at, c.deleted_at, ct.depth + 1
                FROM categorias c
                INNER JOIN category_tree ct ON c.parent_id = ct.id
                WHERE c.deleted_at IS NULL AND ct.depth < :depth_limit
            )
            SELECT id, nombre, descripcion, parent_id, created_at, updated_at, deleted_at
            FROM category_tree
            ORDER BY parent_id, nombre
        """)
        
        result = await self.session.execute(query, {"depth_limit": depth_limit})
        rows = result.fetchall()
        
        # Reconstruct ORM objects from raw rows
        categories_by_id = {}
        for row in rows:
            cat = Categoria(
                id=row[0],
                nombre=row[1],
                descripcion=row[2],
                parent_id=row[3],
                created_at=row[4],
                updated_at=row[5],
                deleted_at=row[6]
            )
            categories_by_id[cat.id] = cat
        
        # Build parent-child relationships
        for cat_id, cat in categories_by_id.items():
            if cat.parent_id and cat.parent_id in categories_by_id:
                parent = categories_by_id[cat.parent_id]
                if not hasattr(parent, 'children') or parent.children is None:
                    parent.children = []
                parent.children.append(cat)
        
        # Return only root categories
        roots = [cat for cat in categories_by_id.values() if cat.parent_id is None]
        return sorted(roots, key=lambda c: c.nombre)
    
    async def validate_no_cycle(
        self, categoria_id: int, new_parent_id: int, depth_limit: int = 20
    ) -> bool:
        """
        Check if assigning new_parent_id as parent of categoria_id creates a cycle.
        
        Uses a recursive CTE traversal from new_parent_id up to root.
        If depth > depth_limit, raises error (prevents infinite loops on cycles).
        
        Args:
            categoria_id: Category being updated
            new_parent_id: Proposed parent ID
            depth_limit: Maximum allowed tree depth (default 20)
            
        Returns:
            True if valid (no cycle detected), False otherwise
            
        Raises:
            ValueError: If cycle detected or depth limit exceeded
        """
        # Early check: self-reference
        if categoria_id == new_parent_id:
            raise ValueError("A category cannot be its own parent")
        
        # Use CTE to traverse from new_parent_id up to root, counting depth
        # If we encounter categoria_id in the path, there's a cycle
        query = text("""
            WITH RECURSIVE ancestors AS (
                SELECT id, parent_id, 1 as depth
                FROM categorias
                WHERE id = :new_parent_id AND deleted_at IS NULL
                
                UNION ALL
                
                SELECT c.id, c.parent_id, a.depth + 1
                FROM categorias c
                INNER JOIN ancestors a ON c.id = a.parent_id
                WHERE a.depth < :depth_limit AND c.deleted_at IS NULL
            )
            SELECT id, depth FROM ancestors WHERE id = :categoria_id
        """)
        
        result = await self.session.execute(
            query,
            {
                "categoria_id": categoria_id,
                "new_parent_id": new_parent_id,
                "depth_limit": depth_limit,
            }
        )
        cycle_row = result.first()
        
        if cycle_row:
            raise ValueError(
                f"Cycle detected: cannot set parent_id={new_parent_id} "
                f"for categoria_id={categoria_id}"
            )
        
        # Check if depth limit would be exceeded
        query_depth = text("""
            WITH RECURSIVE ancestors AS (
                SELECT id, parent_id, 1 as depth
                FROM categorias
                WHERE id = :new_parent_id AND deleted_at IS NULL
                
                UNION ALL
                
                SELECT c.id, c.parent_id, a.depth + 1
                FROM categorias c
                INNER JOIN ancestors a ON c.id = a.parent_id
                WHERE a.depth < :depth_limit AND c.deleted_at IS NULL
            )
            SELECT MAX(depth) as max_depth FROM ancestors
        """)
        
        depth_result = await self.session.execute(
            query_depth,
            {
                "new_parent_id": new_parent_id,
                "depth_limit": depth_limit,
            }
        )
        max_depth = depth_result.scalar()
        
        if max_depth and max_depth >= depth_limit:
            raise ValueError(
                f"Tree depth limit ({depth_limit}) would be exceeded. "
                f"Current depth from parent: {max_depth}"
            )
        
        return True
    
    async def count_children(self, categoria_id: int) -> int:
        """
        Count direct children (non-soft-deleted) of a category.
        
        Args:
            categoria_id: Category ID
            
        Returns:
            Number of direct children
        """
        stmt = select(func.count(Categoria.id)).where(
            and_(
                Categoria.parent_id == categoria_id,
                Categoria.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def count_descendants(self, categoria_id: int) -> int:
        """
        Count all descendants (recursive) of a category (non-soft-deleted).
        
        Uses recursive CTE to count all levels.
        
        Args:
            categoria_id: Category ID
            
        Returns:
            Number of all descendants (including children, grandchildren, etc.)
        """
        query = text("""
            WITH RECURSIVE descendants AS (
                SELECT id, parent_id
                FROM categorias
                WHERE parent_id = :categoria_id AND deleted_at IS NULL
                
                UNION ALL
                
                SELECT c.id, c.parent_id
                FROM categorias c
                INNER JOIN descendants d ON c.parent_id = d.id
                WHERE c.deleted_at IS NULL
            )
            SELECT COUNT(*) FROM descendants
        """)
        
        result = await self.session.execute(query, {"categoria_id": categoria_id})
        return result.scalar() or 0
    
    async def has_descendants(self, categoria_id: int) -> bool:
        """
        Check if a category has any descendants (recursive).
        
        Args:
            categoria_id: Category ID
            
        Returns:
            True if has descendants, False otherwise
        """
        count = await self.count_descendants(categoria_id)
        return count > 0
    
    async def count_products_in_category(self, categoria_id: int) -> int:
        """
        Count products in a category (via categoria_id foreign key).
        
        Prepared for when the Producto table is created.
        Currently returns 0 if table doesn't exist (safe during incremental feature development).
        
        Args:
            categoria_id: Category ID
            
        Returns:
            Number of products in category (0 if table doesn't exist)
        """
        try:
            # Try to count products with this categoria_id
            # This query assumes a 'productos' table with 'categoria_id' column exists
            query = text("""
                SELECT COUNT(*) FROM productos
                WHERE categoria_id = :categoria_id AND deleted_at IS NULL
            """)
            result = await self.session.execute(query, {"categoria_id": categoria_id})
            return result.scalar() or 0
        except Exception:
            # Table doesn't exist yet or query failed — return 0 (safe)
            logger.debug(f"Products table not ready, skipping product count for categoria_id={categoria_id}")
            return 0
    
    
