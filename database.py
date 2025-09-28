"""
PostgreSQL Database Manager for Chat Marketplace Service
Singleton pattern ile async PostgreSQL connection management
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, event
from sqlalchemy.pool import NullPool

from src.config import Config
from src.datalayer.model.sqlalchemy_models import Base

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    """Singleton PostgreSQL connection manager"""
    
    _instance: Optional['PostgreSQLManager'] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'PostgreSQLManager':
        if cls._instance is None:
            cls._instance = super(PostgreSQLManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize()
    
    def _initialize(self):
        """Initialize PostgreSQL connection"""
        try:
            config = Config()
            logger.info(f"🔗 Initializing PostgreSQL connection - Host: {config.postgres_host}:{config.postgres_port}")
            
            # Create async engine
            self._engine = create_async_engine(
                config.postgres_url,
                echo=config.postgres_echo,
                pool_size=config.postgres_pool_size,
                max_overflow=config.postgres_max_overflow,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections every hour
                # Use NullPool for testing to avoid connection issues
                poolclass=NullPool if config.app_env == 'test' else None
            )
            
            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            )
            
            # Add event listeners for connection handling
            self._setup_event_listeners()
            
            PostgreSQLManager._initialized = True
            logger.info(f"✅ PostgreSQL connection initialized - {config.postgres_url}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing PostgreSQL connection: {e}")
            raise
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners"""
        
        @event.listens_for(self._engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set connection-level settings for PostgreSQL"""
            if 'postgresql' in str(dbapi_connection.__class__):
                with dbapi_connection.cursor() as cursor:
                    # Set timezone
                    cursor.execute("SET timezone TO 'UTC'")
                    # Set schema search path
                    cursor.execute("SET search_path TO auth, chats, marketplace, public")
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the async engine"""
        if not self._engine:
            raise RuntimeError("PostgreSQL engine not initialized")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory"""
        if not self._session_factory:
            raise RuntimeError("PostgreSQL session factory not initialized")
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session"""
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with transaction management"""
        async with self._session_factory() as session:
            try:
                async with session.begin():
                    yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_all_tables(self):
        """Create all database tables"""
        try:
            async with self._engine.begin() as conn:
                # Create schemas first
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS chats"))
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS marketplace"))
                
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("✅ All database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")
            raise
    
    async def drop_all_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                
            logger.info("✅ All database tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Error dropping database tables: {e}")
            raise
    
    async def health_check(self) -> dict:
        """Check PostgreSQL connection health"""
        try:
            async with self.get_session() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT 1 as health_check"))
                health_value = result.scalar()
                
                # Get version info
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # Get current database name
                db_result = await session.execute(text("SELECT current_database()"))
                database = db_result.scalar()
                
                # Get schema info - simplified approach
                schema_result = await session.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.schemata 
                    WHERE schema_name IN ('auth', 'chats', 'marketplace')
                """))
                schema_count = schema_result.scalar()
                
                return {
                    "status": "healthy" if health_value == 1 else "unhealthy",
                    "database": database,
                    "version": version,
                    "schema_count": schema_count,
                    "pool_size": self._engine.pool.size(),
                    "pool_checked_out": self._engine.pool.checkedout(),
                    "pool_overflow": self._engine.pool.overflow(),
                }
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def wait_for_connection(self, max_retries: int = 30, retry_delay: float = 2.0) -> bool:
        """Wait for PostgreSQL to be available with retry logic"""
        config = Config()
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔄 Attempting to connect to PostgreSQL (attempt {attempt}/{max_retries})")
                
                health = await self.health_check()
                if health["status"] == "healthy":
                    logger.info(f"✅ Successfully connected to PostgreSQL database: {health['database']}")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL connection attempt {attempt} failed: {e}")
                
                if attempt < max_retries:
                    logger.info(f"🕐 Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"❌ Failed to connect to PostgreSQL after {max_retries} attempts")
                    return False
        
        return False
    
    async def close(self):
        """Close the database connection"""
        if self._engine:
            await self._engine.dispose()
            logger.info("✅ PostgreSQL connection closed")

# Singleton instance
postgres_manager = PostgreSQLManager()

# Dependency function for FastAPI
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting PostgreSQL session"""
    async with postgres_manager.get_session() as session:
        yield session

async def get_postgres_transaction_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting PostgreSQL session with transaction"""
    async with postgres_manager.get_transaction_session() as session:
        yield session

# Convenience functions
async def health_check() -> dict:
    """Convenience function for health check"""
    return await postgres_manager.health_check()

async def wait_for_postgres_connection(max_retries: int = 30, retry_delay: float = 2.0) -> bool:
    """Convenience function for waiting for PostgreSQL connection"""
    return await postgres_manager.wait_for_connection(max_retries, retry_delay)

async def create_all_tables():
    """Convenience function for creating all tables"""
    await postgres_manager.create_all_tables()

async def drop_all_tables():
    """Convenience function for dropping all tables"""
    await postgres_manager.drop_all_tables()

__all__ = [
    "PostgreSQLManager",
    "postgres_manager",
    "get_postgres_session",
    "get_postgres_transaction_session",
    "health_check",
    "wait_for_postgres_connection",
    "create_all_tables",
    "drop_all_tables"
]