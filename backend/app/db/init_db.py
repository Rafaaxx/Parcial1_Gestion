"""Initialize database schema - create all tables"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load .env BEFORE importing config
env_file = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_file)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import all models to register them with SQLModel.metadata
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.modules.pagos.model import Pago
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Create all tables in the database"""
    logger.info("Initializing database schema...")
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )
    
    try:
        async with engine.begin() as conn:
            # Create all tables from SQLModel metadata
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
