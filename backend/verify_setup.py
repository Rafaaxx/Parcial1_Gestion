#!/usr/bin/env python
"""Verification script for CHANGE-00a backend setup"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


async def verify_config():
    """Verify Pydantic configuration loads"""
    print("1️⃣  Verifying config...")
    try:
        from app.config import settings

        assert settings.app_name == "Food Store API"
        assert settings.app_version == "0.1.0"
        assert settings.database_url.startswith("postgresql+asyncpg://")
        print("   ✅ Config loaded correctly")
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False


async def verify_database():
    """Verify database connection"""
    print("2️⃣  Verifying database connection...")
    try:
        from sqlalchemy import text

        from app.database import engine

        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        print("   ✅ Database connection successful")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False


async def verify_models():
    """Verify models and mixins"""
    print("3️⃣  Verifying models...")
    try:
        from app.models.mixins import BaseModel, SoftDeleteMixin, TimestampMixin

        # Verify TimestampMixin has timestamp fields
        tm_fields = TimestampMixin.model_fields
        assert "created_at" in tm_fields, "Missing created_at in TimestampMixin"
        assert "updated_at" in tm_fields, "Missing updated_at in TimestampMixin"

        # Verify SoftDeleteMixin
        sdm_fields = SoftDeleteMixin.model_fields
        assert "deleted_at" in sdm_fields, "Missing deleted_at in SoftDeleteMixin"
        assert hasattr(SoftDeleteMixin, "is_deleted"), "Missing is_deleted method"

        # Verify BaseModel combines both
        bm_fields = BaseModel.model_fields
        assert "created_at" in bm_fields, "BaseModel missing created_at"
        assert "deleted_at" in bm_fields, "BaseModel missing deleted_at"
        assert "updated_at" in bm_fields, "BaseModel missing updated_at"

        print("   ✅ Models loaded correctly")
        return True
    except Exception as e:
        print(f"   ❌ Models error: {e}")
        return False


async def verify_repository():
    """Verify BaseRepository"""
    print("4️⃣  Verifying BaseRepository...")
    try:
        import inspect

        from app.repositories.base import BaseRepository

        methods = [
            method
            for method, _ in inspect.getmembers(
                BaseRepository, predicate=inspect.iscoroutinefunction
            )
        ]
        required = ["find", "list_all", "create", "update", "delete", "soft_delete"]

        for method in required:
            assert any(method == m.lower() for m in methods), f"Missing async method: {method}"

        print("   ✅ BaseRepository has all required methods")
        return True
    except Exception as e:
        print(f"   ❌ Repository error: {e}")
        return False


async def verify_uow():
    """Verify Unit of Work"""
    print("5️⃣  Verifying Unit of Work...")
    try:
        from app.uow import UnitOfWork

        # Verify it's an async context manager
        assert hasattr(UnitOfWork, "__aenter__"), "Missing __aenter__"
        assert hasattr(UnitOfWork, "__aexit__"), "Missing __aexit__"

        # Verify it has required methods
        assert hasattr(UnitOfWork, "get_repository"), "Missing get_repository"
        assert hasattr(UnitOfWork, "commit"), "Missing commit"
        assert hasattr(UnitOfWork, "rollback"), "Missing rollback"

        print("   ✅ Unit of Work is properly implemented")
        return True
    except Exception as e:
        print(f"   ❌ UnitOfWork error: {e}")
        return False


async def verify_fastapi():
    """Verify FastAPI application"""
    print("6️⃣  Verifying FastAPI app...")
    try:
        from app.main import app

        # Verify app was created
        assert app.title == "Food Store API", f"Wrong title: {app.title}"

        # Verify routes exist
        routes = [route.path for route in app.routes]
        assert "/health" in routes, "Missing /health route"
        assert "/" in routes, "Missing / route"

        # Verify exception handlers registered
        assert len(app.exception_handlers) > 0, "No exception handlers"

        # Verify middleware
        assert len(app.user_middleware) > 0, "No middleware registered"

        print("   ✅ FastAPI app configured correctly")
        return True
    except Exception as e:
        print(f"   ❌ FastAPI error: {e}")
        return False


async def verify_exceptions():
    """Verify exception handling"""
    print("7️⃣  Verifying exceptions...")
    try:
        from app.exceptions import (
            AppException,
            ConflictError,
            DatabaseError,
            ForbiddenError,
            NotFoundError,
            RateLimitError,
            UnauthorizedError,
            ValidationError,
        )

        # Verify exception hierarchy
        assert issubclass(
            ValidationError, AppException
        ), "ValidationError not subclass of AppException"
        assert issubclass(NotFoundError, AppException), "NotFoundError not subclass of AppException"

        print("   ✅ Exception classes configured")
        return True
    except Exception as e:
        print(f"   ❌ Exceptions error: {e}")
        return False


async def verify_dependencies():
    """Verify dependency injection"""
    print("8️⃣  Verifying dependencies...")
    try:
        from app.dependencies import get_db, get_uow

        # Verify they exist and are callable
        assert callable(get_db), "get_db not callable"
        assert callable(get_uow), "get_uow not callable"

        print("   ✅ Dependencies configured")
        return True
    except Exception as e:
        print(f"   ❌ Dependencies error: {e}")
        return False


async def main():
    """Run all verifications"""
    print("\n" + "=" * 60)
    print("🔍  CHANGE-00a Backend Setup Verification")
    print("=" * 60 + "\n")

    results = []

    results.append(await verify_config())
    results.append(await verify_database())
    results.append(await verify_models())
    results.append(await verify_repository())
    results.append(await verify_uow())
    results.append(await verify_fastapi())
    results.append(await verify_exceptions())
    results.append(await verify_dependencies())

    print("\n" + "=" * 60)

    if all(results):
        print("✅ ALL VERIFICATIONS PASSED")
        print("=" * 60)
        return 0
    else:
        failed = sum(1 for r in results if not r)
        print(f"❌ {failed} VERIFICATION(S) FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
