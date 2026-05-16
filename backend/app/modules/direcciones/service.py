"""DireccionService — business logic for delivery address management.

Implements:
  - Ownership validation (usuario_id from JWT vs direccion.usuario_id)
  - Auto-assign es_principal on first address (RN-DI01)
  - Atomic default address switching (RN-DI02)
  - Reassign default on delete of current default (REQ-DI-26)
  - Trimming/cleaning input fields
"""

from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.exceptions import AppException, ConflictError, NotFoundError, ValidationError
from app.models.direccion_entrega import DireccionEntrega
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionListResponse,
    DireccionRead,
    DireccionUpdate,
)


class DireccionService:
    """
    Business logic for address management.

    Key responsibilities:
    - Ownership validation (usuario_id from JWT vs direccion.usuario_id)
    - Auto-assign es_principal on first address (RN-DI01)
    - Atomic default address switching (RN-DI02)
    - Reassign default on delete of current default (REQ-DI-26)
    - Trimming/cleaning input fields
    """

    def __init__(self, uow):
        """
        Initialize service with UnitOfWork.

        Args:
            uow: UnitOfWork instance providing access to repositories
        """
        self.uow = uow

    # ── Input Sanitization ────────────────────────────────────────────────────

    def _trim_fields(self, data) -> tuple[Optional[str], str]:
        """
        Trim whitespace from alias and linea1.

        Rules:
        - alias: if empty after trim → None
        - linea1: if empty after trim → raise ValidationError(422)

        Args:
            data: Schema with alias and/or linea1 fields

        Returns:
            Tuple of (alias_trimmed, linea1_trimmed)

        Raises:
            ValidationError: If linea1 is empty after trim
        """
        alias = data.alias.strip() if data.alias else None
        if alias == "":
            alias = None

        if data.linea1 is not None:
            linea1 = data.linea1.strip()
            if not linea1:
                raise ValidationError("linea1 no puede estar vacío")
        else:
            linea1 = None

        return alias, linea1

    def _validate_update_has_fields(self, data: DireccionUpdate) -> None:
        """
        Validate that at least one field is provided for update.

        Args:
            data: DireccionUpdate schema

        Raises:
            ValidationError: If no fields to update
        """
        update_dict = data.model_dump(exclude_none=True)
        if not update_dict:
            raise ValidationError("No hay campos para actualizar")

    # ── CRUD Operations ───────────────────────────────────────────────────────

    async def create_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        """
        Create a new delivery address.

        Business rules:
        1. Trim alias and linea1
        2. If alias empty after trim → treat as None
        3. If linea1 empty after trim → 422
        4. If user has 0 addresses → set es_principal=True (RN-DI01)
        5. Create via repository

        Args:
            usuario_id: Authenticated user's ID (from JWT)
            data: DireccionCreate schema

        Returns:
            DireccionRead response

        Raises:
            ValidationError: If linea1 is empty after trim
        """
        # Trim fields
        alias, linea1 = self._trim_fields(data)

        # Count existing addresses
        count = await self.uow.direcciones.count_by_usuario(usuario_id)

        # First address → auto-assign as default (RN-DI01)
        es_principal = count == 0

        # Build model instance
        direccion_model = DireccionEntrega(
            usuario_id=usuario_id,
            alias=alias,
            linea1=linea1,
            es_principal=es_principal,
        )

        # Create via repository
        direccion = await self.uow.direcciones.create(direccion_model)

        return DireccionRead.model_validate(direccion)

    async def list_direcciones(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> DireccionListResponse:
        """
        List active addresses for the authenticated user.

        Args:
            usuario_id: Authenticated user's ID (from JWT)
            skip: Pagination offset
            limit: Page size

        Returns:
            DireccionListResponse with paginated results
        """
        items, total = await self.uow.direcciones.find_by_usuario(
            usuario_id, skip=skip, limit=limit
        )

        return DireccionListResponse(
            items=[DireccionRead.model_validate(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_direccion(
        self, direccion_id: int, usuario_id: int, data: DireccionUpdate
    ) -> DireccionRead:
        """
        Update an existing delivery address.

        Business rules:
        1. Trim fields
        2. Validate at least one field to update (422 if empty)
        3. Verify ownership + existence → 404 if not found
        4. Update only provided fields

        Args:
            direccion_id: Address ID to update
            usuario_id: Authenticated user's ID (from JWT)
            data: DireccionUpdate schema

        Returns:
            Updated DireccionRead

        Raises:
            NotFoundError: If address not found, not owned, or soft-deleted
            ValidationError: If no fields provided or linea1 is empty after trim
        """
        # Validate at least one field
        self._validate_update_has_fields(data)

        # Verify ownership + existence
        direccion = await self.uow.direcciones.find_user_direccion(direccion_id, usuario_id)
        if not direccion:
            raise NotFoundError("Dirección no encontrada")

        # Build update dict from provided fields (exclude None)
        update_dict = data.model_dump(exclude_none=True)

        # Trim fields if present
        if "alias" in update_dict:
            alias = update_dict["alias"].strip() if update_dict["alias"] else None
            if alias == "":
                alias = None
            update_dict["alias"] = alias

        if "linea1" in update_dict:
            linea1 = update_dict["linea1"].strip()
            if not linea1:
                raise ValidationError("linea1 no puede estar vacío")
            update_dict["linea1"] = linea1

        # Update via repository
        updated = await self.uow.direcciones.update(direccion_id, update_dict)
        if not updated:
            raise NotFoundError("Dirección no encontrada")

        return DireccionRead.model_validate(updated)

    async def delete_direccion(self, direccion_id: int, usuario_id: int) -> None:
        """
        Soft-delete a delivery address.

        Business rules:
        1. Verify ownership + existence → 404 if not found
        2. If deleting the default address:
           a. Find most recent active address
           b. If found → reassign es_principal=True
        3. Soft-delete the address

        All within the same transaction (commit in router).

        Args:
            direccion_id: Address ID to delete
            usuario_id: Authenticated user's ID (from JWT)

        Raises:
            NotFoundError: If address not found, not owned, or soft-deleted
        """
        # Verify ownership + existence
        direccion = await self.uow.direcciones.find_user_direccion(direccion_id, usuario_id)
        if not direccion:
            raise NotFoundError("Dirección no encontrada")

        # If deleting the default, reassign to most recent active (REQ-DI-26)
        if direccion.es_principal:
            most_recent = await self.uow.direcciones.find_most_recent_active(
                usuario_id, exclude_id=direccion_id
            )
            if most_recent:
                await self.uow.direcciones.set_es_principal(most_recent.id, True)

        # Soft-delete
        await self.uow.direcciones.soft_delete(direccion_id)

    async def set_predeterminada(self, direccion_id: int, usuario_id: int) -> DireccionRead:
        """
        Set an address as the default (predeterminada) — ATOMIC transaction.

        Business rules:
        1. Verify ownership + existence → 404 if not found
        2. If already es_principal=True → return current (idempotent, REQ-DI-30)
        3. Unset previous default
        4. Set new default
        5. Reload and return updated address

        All within the same transaction (atomic via UoW).

        Args:
            direccion_id: Address ID to set as default
            usuario_id: Authenticated user's ID (from JWT)

        Returns:
            Updated DireccionRead with es_principal=True

        Raises:
            NotFoundError: If address not found, not owned, or soft-deleted
            ConflictError: If unique partial index violation (race condition)
        """
        try:
            # Verify ownership + existence
            direccion = await self.uow.direcciones.find_user_direccion(direccion_id, usuario_id)
            if not direccion:
                raise NotFoundError("Dirección no encontrada")

            # Idempotent: if already default, return current (REQ-DI-30)
            if direccion.es_principal:
                return DireccionRead.model_validate(direccion)

            # Atomic: unset previous + set new in same transaction
            await self.uow.direcciones.unset_previous_default(usuario_id)
            await self.uow.direcciones.set_es_principal(direccion_id, True)

            # Reload and return updated
            updated = await self.uow.direcciones.find(direccion_id)
            if not updated:
                raise NotFoundError("Dirección no encontrada")

            return DireccionRead.model_validate(updated)
        except IntegrityError:
            raise ConflictError("Ya existe una dirección predeterminada")
