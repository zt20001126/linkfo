from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_search import ProductSearchRecord
from app.schemas.product_search import EchoTikProductListParams, ProductSearchQuery


class ProductSearchRepository:
    """选品查询记录仓储，只负责查询记录表的写入和事务提交。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_record(
        self,
        *,
        prompt: str,
        query: ProductSearchQuery,
        params: EchoTikProductListParams,
        response_summary: dict[str, Any],
        status: str,
        error_code: str | None = None,
    ) -> ProductSearchRecord:
        """保存脱敏查询记录，避免把密钥、鉴权头或第三方完整敏感响应落库。"""

        record = ProductSearchRecord(
            prompt=prompt,
            region=query.region,
            keyword=query.keyword,
            category_name=query.category_name,
            category_id=params.category_id,
            category_l2_id=params.category_l2_id,
            category_l3_id=params.category_l3_id,
            page_num=params.page_num,
            page_size=params.page_size,
            product_sort_field=params.product_sort_field,
            sort_type=params.sort_type,
            request_params=params.model_dump(exclude_none=True),
            response_summary=response_summary,
            status=status,
            error_code=error_code,
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record
