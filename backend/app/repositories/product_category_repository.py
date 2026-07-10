from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_search import ProductCategoryMapping
from app.schemas.product_search import ProductCategoryMappingDTO


class ProductCategoryRepository:
    """商品分类映射仓储，只负责分类映射表的查询和持久化转换。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_enabled_mapping(self, region: str, category_name: str) -> ProductCategoryMappingDTO | None:
        """按地区和分类名称查询启用中的 EchoTik 分类映射。"""

        statement = (
            select(ProductCategoryMapping)
            .where(ProductCategoryMapping.region == region)
            .where(ProductCategoryMapping.category_name == category_name)
            .where(ProductCategoryMapping.enabled.is_(True))
            .limit(1)
        )
        result = await self._session.execute(statement)
        mapping = result.scalar_one_or_none()
        if mapping is None:
            return None

        return ProductCategoryMappingDTO(
            category_name=mapping.category_name,
            category_id=mapping.category_id,
            category_l2_id=mapping.category_l2_id,
            category_l3_id=mapping.category_l3_id,
        )
