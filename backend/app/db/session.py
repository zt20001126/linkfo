from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """懒加载数据库引擎，避免未启用数据库时强依赖 asyncpg 或本地 PostgreSQL。"""

    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database.url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """懒加载数据库会话工厂，统一复用同一个异步引擎。"""

    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession | None, None]:
    """提供可选数据库会话，未启用数据库时返回 None，避免路由层感知持久化细节。"""

    if not settings.database.enabled:
        yield None
        return

    async with get_session_factory()() as session:
        yield session
