"""PerfilService — business logic for customer profile management.

Stateless service injected via method parameters.
Uses existing AuthRepository and RefreshTokenRepository from the auth module.
"""
import logging

from app.uow import UnitOfWork
from app.security import hash_password, verify_password
from app.exceptions import NotFoundError, ValidationError, UnauthorizedError
from app.models.usuario import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.perfil.schemas import PerfilRead, PerfilUpdate, PasswordChange
from app.modules.refreshtokens.repository import RefreshTokenRepository

logger = logging.getLogger(__name__)


class PerfilService:
    """Stateless service for customer profile operations."""

    async def get_profile(
        self,
        current_user: Usuario,
        uow: UnitOfWork,
        auth_repo: AuthRepository,
    ) -> PerfilRead:
        """Return the authenticated user's full profile.

        Args:
            current_user: Authenticated Usuario from JWT.
            uow: Active UnitOfWork.
            auth_repo: AuthRepository for user lookup with roles.

        Returns:
            PerfilRead with all profile fields.
        """
        # Reload user with roles from DB for fresh data
        usuario = await auth_repo.find_with_roles(current_user.id)
        if usuario is None:
            raise NotFoundError("Usuario no encontrado")

        roles = [ur.rol_codigo for ur in (usuario.usuario_roles or [])]
        return PerfilRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            telefono=usuario.telefono,
            roles=roles,
            fecha_registro=usuario.created_at,
        )

    async def update_profile(
        self,
        current_user: Usuario,
        data: PerfilUpdate,
        uow: UnitOfWork,
    ) -> PerfilRead:
        """Update the authenticated user's profile fields.

        Only nombre, apellido, and telefono can be updated.
        Email is immutable (used as identifier per US-062).

        Args:
            current_user: Authenticated Usuario from JWT.
            data: PerfilUpdate with optional fields.
            uow: Active UnitOfWork.

        Returns:
            Updated PerfilRead.

        Raises:
            ValidationError: If no fields provided for update (422).
        """
        # Validate at least one field
        update_dict = data.model_dump(exclude_none=True)
        if not update_dict:
            raise ValidationError("No hay campos para actualizar")

        # Build roles list from current user
        roles = [ur.rol_codigo for ur in (current_user.usuario_roles or [])]

        # Reload user and update
        repo = AuthRepository(uow.session, Usuario)
        usuario = await repo.find_with_roles(current_user.id)
        if usuario is None:
            raise NotFoundError("Usuario no encontrado")

        # Apply updates
        for field, value in update_dict.items():
            setattr(usuario, field, value)

        uow.session.add(usuario)
        await uow.session.flush()
        await uow.session.refresh(usuario)

        return PerfilRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            telefono=usuario.telefono,
            roles=roles,
            fecha_registro=usuario.created_at,
        )

    async def change_password(
        self,
        current_user: Usuario,
        data: PasswordChange,
        uow: UnitOfWork,
    ) -> dict:
        """Change the authenticated user's password.

        Validates current password, hashes the new one, and revokes ALL
        existing refresh tokens to force re-login (US-063).

        Args:
            current_user: Authenticated Usuario from JWT.
            data: PasswordChange with actual and new password.
            uow: Active UnitOfWork.

        Returns:
            Success message dict.

        Raises:
            UnauthorizedError: If password_actual doesn't match (401).
            ValidationError: If password_nueva doesn't meet requirements.
        """
        # Verify current password
        if not verify_password(data.password_actual, current_user.password_hash):
            raise UnauthorizedError("Contraseña actual incorrecta")

        # Hash new password
        new_hash = hash_password(data.password_nueva)

        # Update password
        repo = AuthRepository(uow.session, Usuario)
        usuario = await repo.find_with_roles(current_user.id)
        if usuario is None:
            raise NotFoundError("Usuario no encontrado")

        usuario.password_hash = new_hash
        uow.session.add(usuario)

        # Revoke all existing refresh tokens (force re-login per US-063)
        refresh_repo = RefreshTokenRepository(uow.session)
        await refresh_repo.revoke_all_for_user(usuario.id)

        await uow.session.flush()

        logger.info(f"Password changed for user {usuario.id} — all tokens revoked")
        return {
            "message": "Contraseña actualizada exitosamente",
            "requires_relogin": True,
        }
