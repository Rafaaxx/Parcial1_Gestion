"""FastAPI router for customer profile management.

Three endpoints:
  - GET  /api/v1/perfil          → View profile
  - PUT  /api/v1/perfil          → Update profile (nombre, apellido, telefono)
  - PUT  /api/v1/perfil/password → Change password

All endpoints require authentication (any active role).
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_uow, get_current_user
from app.uow import UnitOfWork
from app.models.usuario import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.perfil.schemas import PerfilRead, PerfilUpdate, PasswordChange, PasswordChangeResponse
from app.modules.perfil.service import PerfilService
from app.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/perfil", tags=["Perfil"])


def _get_auth_repo(uow: UnitOfWork = Depends(get_uow)) -> AuthRepository:
    """Factory for AuthRepository bound to current UoW."""
    return AuthRepository(uow.session, Usuario)


# ── GET /perfil ──────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=PerfilRead,
    summary="Obtener perfil del usuario autenticado",
    responses={
        200: {"description": "Perfil del usuario"},
        401: {"description": "No autenticado"},
    },
)
async def get_perfil(
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    auth_repo: AuthRepository = Depends(_get_auth_repo),
) -> PerfilRead:
    """Obtener los datos del perfil del usuario autenticado.

    Retorna: id, nombre, apellido, email, teléfono, roles y fecha de registro.
    No requiere roles específicos — cualquier usuario activo puede ver su perfil.
    """
    try:
        service = PerfilService()
        result = await service.get_profile(
            current_user=current_user,
            uow=uow,
            auth_repo=auth_repo,
        )
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"GET /perfil failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ── PUT /perfil ──────────────────────────────────────────────────────────────


@router.put(
    "",
    response_model=PerfilRead,
    summary="Actualizar datos del perfil",
    responses={
        200: {"description": "Perfil actualizado exitosamente"},
        401: {"description": "No autenticado"},
        422: {"description": "Error de validación (sin campos o formato inválido)"},
    },
)
async def update_perfil(
    data: PerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> PerfilRead:
    """Actualizar nombre, apellido y/o teléfono del usuario autenticado.

    - Todos los campos son opcionales, pero al menos uno es requerido.
    - El email NO se puede modificar (es el identificador de cuenta).
    """
    try:
        service = PerfilService()
        result = await service.update_profile(
            current_user=current_user,
            data=data,
            uow=uow,
        )
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"PUT /perfil failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ── PUT /perfil/password ─────────────────────────────────────────────────────


@router.put(
    "/password",
    response_model=PasswordChangeResponse,
    summary="Cambiar contraseña",
    responses={
        200: {"description": "Contraseña actualizada exitosamente"},
        401: {"description": "Contraseña actual incorrecta o no autenticado"},
        422: {"description": "Nueva contraseña no cumple requisitos (mín 8 caracteres)"},
    },
)
async def change_password(
    data: PasswordChange,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> dict:
    """Cambiar la contraseña del usuario autenticado.

    - Valida que password_actual sea correcta.
    - Al cambiar, se revocan TODOS los refresh tokens (forzar re-login).
    """
    try:
        service = PerfilService()
        result = await service.change_password(
            current_user=current_user,
            data=data,
            uow=uow,
        )
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"PUT /perfil/password failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
