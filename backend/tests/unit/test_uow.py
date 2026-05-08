"""Tests for UnitOfWork atomic transaction management."""
import pytest
from app.uow import UnitOfWork
from tests.models import TestModel, UoWTestModel


@pytest.mark.asyncio
async def test_uow_commit(test_db_session):
    """UoW commit persists all changes atomically."""
    uow = UnitOfWork(test_db_session)
    async with uow:
        repo = uow.get_repository(TestModel)
        entity = TestModel(name="uow_commit", value=1)
        await repo.create(entity)

    # Verify data is persisted
    repo2 = UnitOfWork(test_db_session).get_repository(TestModel)
    found = await repo2.find(entity.id)
    assert found is not None
    assert found.name == "uow_commit"


@pytest.mark.asyncio
async def test_uow_rollback_on_error(test_db_session):
    """UoW rolls back all changes when an exception occurs."""
    entity_id = None

    try:
        uow = UnitOfWork(test_db_session)
        async with uow:
            repo = uow.get_repository(TestModel)
            entity = TestModel(name="uow_rollback", value=2)
            created = await repo.create(entity)
            entity_id = created.id
            raise ValueError("Simulated failure")
    except ValueError:
        pass  # Expected

    # Entity should NOT have been persisted
    if entity_id is not None:
        repo2 = UnitOfWork(test_db_session).get_repository(TestModel)
        found = await repo2.find(entity_id)
        assert found is None, "Entity was persisted despite rollback"


@pytest.mark.asyncio
async def test_uow_multiple_repositories(test_db_session):
    """UoW coordinates changes across multiple repositories."""
    uow = UnitOfWork(test_db_session)
    async with uow:
        repo_a = uow.get_repository(TestModel)
        repo_b = uow.get_repository(UoWTestModel)

        entity_a = TestModel(name="multi_a", value=10)
        entity_b = UoWTestModel(name="multi_b")

        created_a = await repo_a.create(entity_a)
        created_b = await repo_b.create(entity_b)

    # Both entities should be persisted
    check_uow = UnitOfWork(test_db_session)
    found_a = await check_uow.get_repository(TestModel).find(created_a.id)
    found_b = await check_uow.get_repository(UoWTestModel).find(created_b.id)

    assert found_a is not None
    assert found_a.name == "multi_a"
    assert found_b is not None
    assert found_b.name == "multi_b"
