"""FastAPI dependency injection setup"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import async_session_factory, get_db
from app.uow import UnitOfWork

logger = logging.getLogger(__name__)


async def get_uow(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency for FastAPI to inject Unit of Work
    
    Usage in an endpoint:
        @app.post("/orders")
        async def create_order(order_data: CreateOrderRequest, uow: UnitOfWork = Depends(get_uow)):
            async with uow:
                order = await uow.get_repository(Order).create(order_data)
    
    Args:
        session: AsyncSession from get_db dependency
        
    Yields:
        UnitOfWork instance
    """
    uow = UnitOfWork(session)
    try:
        yield uow
    finally:
        logger.debug("UnitOfWork dependency cleanup")
