"""Tests for BaseRepository[T] generic CRUD operations."""

import pytest
from sqlalchemy import func, select

from app.repositories.base import BaseRepository
from tests.models import TestModel


@pytest.mark.asyncio
async def test_create(test_db_session):
    """Create a new entity and verify it gets an auto-generated id."""
    repo = BaseRepository(test_db_session, TestModel)
    entity = TestModel(name="test_create", value=42)
    created = await repo.create(entity)

    assert created.id is not None
    assert created.name == "test_create"
    assert created.value == 42


@pytest.mark.asyncio
async def test_find(test_db_session):
    """Find an entity by its primary key."""
    repo = BaseRepository(test_db_session, TestModel)
    entity = TestModel(name="test_find", value=7)
    created = await repo.create(entity)

    found = await repo.find(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "test_find"
    assert found.value == 7


@pytest.mark.asyncio
async def test_find_not_found(test_db_session):
    """Find a non-existent id returns None."""
    repo = BaseRepository(test_db_session, TestModel)
    result = await repo.find(99999)
    assert result is None


@pytest.mark.asyncio
async def test_list_all(test_db_session):
    """List all entities returns the expected count."""
    repo = BaseRepository(test_db_session, TestModel)
    for i in range(5):
        await repo.create(TestModel(name=f"item_{i}", value=i))

    items, total = await repo.list_all()
    assert total == 5
    assert len(items) == 5
    names = [item.name for item in items]
    assert "item_0" in names
    assert "item_4" in names


@pytest.mark.asyncio
async def test_pagination(test_db_session):
    """Pagination correctly limits and offsets results."""
    repo = BaseRepository(test_db_session, TestModel)
    for i in range(20):
        await repo.create(TestModel(name=f"page_item_{i}", value=i))

    # First page of 5
    page1, total = await repo.list_all(skip=0, limit=5)
    assert total == 20
    assert len(page1) == 5

    # Second page of 5
    page2, _ = await repo.list_all(skip=5, limit=5)
    assert len(page2) == 5
    # Items should differ from page1
    assert page1[0].id != page2[0].id


@pytest.mark.asyncio
async def test_filters(test_db_session):
    """Filters narrow results down to matching entities."""
    repo = BaseRepository(test_db_session, TestModel)
    await repo.create(TestModel(name="alpha", value=10))
    await repo.create(TestModel(name="beta", value=20))
    await repo.create(TestModel(name="gamma", value=10))

    # Filter by value
    items, total = await repo.list_all(filters={"value": 10})
    assert total == 2
    assert len(items) == 2
    assert all(item.value == 10 for item in items)

    # Filter by name
    items, total = await repo.list_all(filters={"name": "beta"})
    assert total == 1
    assert items[0].name == "beta"


@pytest.mark.asyncio
async def test_update(test_db_session):
    """Update modifies entity fields and returns the updated version."""
    repo = BaseRepository(test_db_session, TestModel)
    entity = await repo.create(TestModel(name="before", value=1))
    original_id = entity.id

    updated = await repo.update(original_id, {"name": "after", "value": 99})
    assert updated is not None
    assert updated.name == "after"
    assert updated.value == 99
    assert updated.id == original_id


@pytest.mark.asyncio
async def test_soft_delete(test_db_session):
    """Soft-delete sets deleted_at and find() excludes soft-deleted records."""
    repo = BaseRepository(test_db_session, TestModel)
    entity = await repo.create(TestModel(name="to_delete", value=0))

    # Soft delete
    deleted = await repo.soft_delete(entity.id)
    assert deleted is not None
    assert deleted.deleted_at is not None

    # Should NOT be found by find() (excludes soft-deleted)
    found = await repo.find(entity.id)
    assert found is None

    # Should NOT appear in list_all
    items, total = await repo.list_all()
    assert total == 0

    # But should still exist via direct get
    raw = await test_db_session.get(TestModel, entity.id)
    assert raw is not None
    assert raw.deleted_at is not None


@pytest.mark.asyncio
async def test_exists(test_db_session):
    """Exists returns True for existing entities, False otherwise."""
    repo = BaseRepository(test_db_session, TestModel)
    entity = await repo.create(TestModel(name="exists_check", value=1))

    assert await repo.exists(entity.id) is True
    assert await repo.exists(99999) is False

    # Soft-deleted records should return False
    await repo.soft_delete(entity.id)
    assert await repo.exists(entity.id) is False


@pytest.mark.asyncio
async def test_count(test_db_session):
    """Count returns the total number of non-deleted entities."""
    repo = BaseRepository(test_db_session, TestModel)
    for i in range(8):
        await repo.create(TestModel(name=f"count_{i}", value=i))

    count = await repo.count()
    assert count == 8

    # Count with filter
    count_filtered = await repo.count(filters={"value": 0})
    assert count_filtered == 1
