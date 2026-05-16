"""AuthRepository — extends BaseRepository[Usuario] with auth-specific queries."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel

from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.repositories.base import BaseRepository


class AuthRepository(BaseRepository[Usuario]):
    """Repository for user authentication operations.

    Extends the generic BaseRepository with:
      - ``find_by_email``: unique email lookup.
      - ``create_with_roles``: atomic user + role assignment creation.
    """

    async def find_by_email(self, email: str) -> Optional[Usuario]:
        """Find a user by their email address (unique), eagerly loading roles.

        Args:
            email: The email to search for.

        Returns:
            Usuario instance (with usuario_roles loaded) or None if not found.
        """
        query = (
            select(Usuario)
            .where(Usuario.email == email)
            .where(Usuario.deleted_at.is_(None))
            .options(selectinload(Usuario.usuario_roles))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_with_roles(self, usuario_id: int) -> Optional[Usuario]:
        """Find a user by ID, eagerly loading roles.

        Args:
            usuario_id: The user's primary key.

        Returns:
            Usuario instance (with usuario_roles loaded) or None if not found.
        """
        query = (
            select(Usuario)
            .where(Usuario.id == usuario_id)
            .where(Usuario.deleted_at.is_(None))
            .options(selectinload(Usuario.usuario_roles))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def create_with_roles(
        self,
        usuario: Usuario,
        roles: list[str],
        asignado_por_id: Optional[int] = None,
    ) -> Usuario:
        """Create a user and assign roles in the same transaction.

        Args:
            usuario: The Usuario instance to create (without id).
            roles: List of role codes to assign (e.g. ["CLIENT"]).
            asignado_por_id: Who assigned the role (None for self-registration).

        Returns:
            The created Usuario with generated id.
        """
        # Create the user first
        created = await self.create(usuario)

        # Assign each role
        for rol_codigo in roles:
            usuario_rol = UsuarioRol(
                usuario_id=created.id,
                rol_codigo=rol_codigo,
                asignado_por_id=asignado_por_id,
            )
            self.session.add(usuario_rol)

        await self.session.flush()
        return created
