import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.product_category_cache import ProductCategoryCache
from app.cache.product_search_cache import ProductSearchCache
from app.common.constants import SEARCH_RECORD_STATUS_FAILED, SEARCH_RECORD_STATUS_SKIPPED, SEARCH_RECORD_STATUS_SUCCESS
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.exceptions.business_exception import BusinessException
from app.repositories.product_category_repository import ProductCategoryRepository
from app.repositories.product_search_repository import ProductSearchRepository
from app.schemas.product_search import (
    EchoTikProductListParams,
    ProductCategoryMappingDTO,
    ProductSearchData,
    ProductSearchOutcome,
    ProductSearchQuery,
    ProductSearchRequest,
)
from app.services.echotik_product_service import EchoTikProductService
from app.services.prompt_parser_service import PromptParserService

logger = logging.getLogger(__name__)


class ProductSearchService:
    """选品搜索编排服务，负责串联提示词解析和 EchoTik 商品服务。"""

    def __init__(
        self,
        prompt_parser_service: PromptParserService,
        echotik_product_service: EchoTikProductService,
        product_search_cache: ProductSearchCache,
        product_category_cache: ProductCategoryCache,
        product_search_repository: ProductSearchRepository | None = None,
        product_category_repository: ProductCategoryRepository | None = None,
    ) -> None:
        self._prompt_parser_service = prompt_parser_service
        self._echotik_product_service = echotik_product_service
        self._product_search_cache = product_search_cache
        self._product_category_cache = product_category_cache
        self._product_search_repository = product_search_repository
        self._product_category_repository = product_category_repository

    async def search(self, request: ProductSearchRequest) -> ProductSearchOutcome:
        """执行选品搜索。

        Step 1: 校验并保留用户提示词。
        Step 2: 解析提示词并解析可选分类映射。
        Step 3: 构造 EchoTik 商品列表参数，优先读取 Redis 缓存。
        Step 4: 缓存未命中时调用 EchoTik 商品服务并写入安全查询记录。
        Step 5: 组装 route 可直接返回的统一响应输出。
        """

        prompt = request.prompt.strip()
        if not prompt:
            raise BusinessException(code="INVALID_PROMPT", message="请传入 prompt 字段")

        query = self._prompt_parser_service.parse_product_search_prompt(prompt)
        category_mapping = await self._resolve_category_mapping(query.region, query.category_name)
        echotik_params = self._prompt_parser_service.build_echotik_product_list_params(query, category_mapping)

        cached_result = await self._product_search_cache.get_result(echotik_params)
        cache_hit = cached_result is not None

        if cached_result is not None:
            result = cached_result
        else:
            try:
                result = await self._echotik_product_service.search_products(echotik_params)
            except BusinessException as exc:
                await self._save_record_safely(
                    prompt=prompt,
                    query=query,
                    params=echotik_params,
                    response_summary={"itemsCount": 0, "implemented": False, "cacheHit": False},
                    status=SEARCH_RECORD_STATUS_FAILED,
                    error_code=exc.code,
                )
                raise
            await self._product_search_cache.set_result(echotik_params, result)

        response_data = ProductSearchData(
            prompt=prompt,
            query=query,
            echotikParams=echotik_params,
            items=result.items,
        )
        await self._save_record_safely(
            prompt=prompt,
            query=query,
            params=echotik_params,
            response_summary={
                "itemsCount": len(result.items),
                "implemented": result.implemented,
                "cacheHit": cache_hit,
            },
            status=SEARCH_RECORD_STATUS_SUCCESS if result.implemented else SEARCH_RECORD_STATUS_SKIPPED,
        )
        return ProductSearchOutcome(
            code="SUCCESS" if result.implemented else "BACKEND_SKELETON_READY",
            message=None if result.implemented else "后端基础框架已连通，EchoTik API 调用默认未启用",
            data=response_data,
        )

    async def _resolve_category_mapping(self, region: str, category_name: str) -> ProductCategoryMappingDTO | None:
        """解析分类映射，先查 Redis，再查数据库，找不到时不向 EchoTik 提交分类 ID。"""

        if not category_name:
            return None

        cached_mapping = await self._product_category_cache.get_mapping(region, category_name)
        if cached_mapping is not None:
            return cached_mapping

        if self._product_category_repository is None:
            return None

        mapping = await self._product_category_repository.find_enabled_mapping(region, category_name)
        if mapping is not None:
            await self._product_category_cache.set_mapping(region, mapping)
        return mapping

    async def _save_record_safely(
        self,
        *,
        prompt: str,
        query: ProductSearchQuery,
        params: EchoTikProductListParams,
        response_summary: dict[str, object],
        status: str,
        error_code: str | None = None,
    ) -> None:
        """保存查询记录，持久化失败只写日志，不把数据库异常暴露给前端。"""

        if self._product_search_repository is None:
            return

        try:
            await self._product_search_repository.create_record(
                prompt=prompt,
                query=query,
                params=params,
                response_summary=response_summary,
                status=status,
                error_code=error_code,
            )
        except Exception as exc:
            logger.warning("product_search_record_save_failed error_type=%s", type(exc).__name__)


async def get_product_search_service(
    settings: Settings = Depends(get_settings),
    db_session: AsyncSession | None = Depends(get_db_session),
) -> ProductSearchService:
    """提供选品搜索服务实例，后续可替换为容器或更细粒度依赖注入。"""

    product_search_repository = ProductSearchRepository(db_session) if db_session is not None else None
    product_category_repository = ProductCategoryRepository(db_session) if db_session is not None else None
    return ProductSearchService(
        prompt_parser_service=PromptParserService(),
        echotik_product_service=EchoTikProductService(settings.echotik),
        product_search_cache=ProductSearchCache(settings.redis),
        product_category_cache=ProductCategoryCache(settings.redis),
        product_search_repository=product_search_repository,
        product_category_repository=product_category_repository,
    )
