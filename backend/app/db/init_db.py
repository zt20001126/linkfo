import asyncio

from app.db.base import Base
from app.db.session import get_engine
from app.models.product_search import ProductCategoryMapping, ProductSearchRecord

__all__ = ["ProductCategoryMapping", "ProductSearchRecord", "init_db"]


async def init_db() -> None:
    """开发环境建表入口，用于本地 Docker PostgreSQL 初始化当前阶段所需表结构。"""

    async with get_engine().begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
