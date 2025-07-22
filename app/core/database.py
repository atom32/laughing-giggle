"""
Database configuration and initialization for Park Tycoon Game
"""
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Database settings
settings = get_settings()

# Determine database type and create appropriate URLs
def get_database_urls():
    """Get sync and async database URLs based on the configured database type."""
    base_url = settings.database_url
    
    if base_url.startswith("postgresql://"):
        # PostgreSQL configuration
        sync_url = base_url.replace("postgresql://", "postgresql+psycopg2://")
        async_url = base_url.replace("postgresql://", "postgresql+asyncpg://")
    elif base_url.startswith("sqlite"):
        # SQLite configuration
        if "+aiosqlite" in base_url:
            async_url = base_url
            sync_url = base_url.replace("+aiosqlite", "")
        else:
            sync_url = base_url
            async_url = base_url.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        # Default to the provided URL
        sync_url = base_url
        async_url = base_url
    
    return sync_url, async_url

sync_db_url, async_db_url = get_database_urls()

# Create sync engine for migrations and initial setup
sync_engine = create_engine(
    sync_db_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

# Create async engine for application use
async_engine = create_async_engine(
    async_db_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """
    Get synchronous database session for migrations and setup.
    
    Returns:
        Session: Database session
    """
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_database():
    """
    Initialize database tables and perform initial setup.
    """
    logger.info("Initializing database...")
    
    try:
        # Import all models to ensure they are registered with Base
        from app.models import user, player, livestock, module, item, translation
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
        # Initialize default data
        await _init_default_data()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def _init_default_data():
    """Initialize default data in the database."""
    logger.info("Initializing default data...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Import models
            from app.models.translation import Translation
            from sqlalchemy import text
            
            # Check if translations already exist
            result = await session.execute(
                text("SELECT COUNT(*) FROM translations")
            )
            count = result.scalar()
            
            if count == 0:
                # Add default translations
                default_translations = [
                    # UI translations
                    Translation(key="ui.welcome", language_code="zh", value="欢迎来到公园大亨", category="ui"),
                    Translation(key="ui.welcome", language_code="en", value="Welcome to Park Tycoon", category="ui"),
                    Translation(key="ui.login", language_code="zh", value="登录", category="ui"),
                    Translation(key="ui.login", language_code="en", value="Login", category="ui"),
                    Translation(key="ui.register", language_code="zh", value="注册", category="ui"),
                    Translation(key="ui.register", language_code="en", value="Register", category="ui"),
                    
                    # Module translations
                    Translation(key="module.market", language_code="zh", value="市场", category="module"),
                    Translation(key="module.market", language_code="en", value="Market", category="module"),
                    Translation(key="module.farm", language_code="zh", value="农场", category="module"),
                    Translation(key="module.farm", language_code="en", value="Farm", category="module"),
                    Translation(key="module.slaughterhouse", language_code="zh", value="屠宰场", category="module"),
                    Translation(key="module.slaughterhouse", language_code="en", value="Slaughterhouse", category="module"),
                    Translation(key="module.restaurant", language_code="zh", value="餐厅", category="module"),
                    Translation(key="module.restaurant", language_code="en", value="Restaurant", category="module"),
                    Translation(key="module.photo_studio", language_code="zh", value="摄影棚", category="module"),
                    Translation(key="module.photo_studio", language_code="en", value="Photo Studio", category="module"),
                    Translation(key="module.dungeon", language_code="zh", value="地牢", category="module"),
                    Translation(key="module.dungeon", language_code="en", value="Dungeon", category="module"),
                    Translation(key="module.private_residence", language_code="zh", value="私人住宅", category="module"),
                    Translation(key="module.private_residence", language_code="en", value="Private Residence", category="module"),
                ]
                
                session.add_all(default_translations)
                await session.commit()
                
                logger.info(f"Added {len(default_translations)} default translations")
            
            logger.info("Default data initialization completed")
            
    except Exception as e:
        logger.error(f"Failed to initialize default data: {e}")
        raise