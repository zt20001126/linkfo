import json
import logging
from typing import Any

from app.common.constants import CATEGORY_MAPPING_CACHE_PREFIX
from app.core.config import RedisSettings
from app.schemas.product_search import ProductCategoryMappingDTO

logger = logging.getLogger(__name__)


class ProductCategoryCache:
    """商品分类映射缓存，用于减少重复读取数据库分类映射。"""

    def __init__(self, settings: RedisSettings) -> None:
        self._settings = settings
        self._client: Any | None = None

    async def get_mapping(self, region: str, category_name: str) -> ProductCategoryMappingDTO | None:
        """读取分类映射缓存，Redis 未启用或异常时安全降级为未命中。"""

        if not self._settings.enabled or not category_name:
            return None

        try:
            client = await self._get_client()
            raw_value = await client.get(self._build_key(region, category_name))
        except Exception as exc:  # 缓存异常不能影响主查询流程。
            logger.warning("category_cache_get_failed error_type=%s", type(exc).__name__)
            return None

        if raw_value is None:
            return None
        return ProductCategoryMappingDTO(**json.loads(raw_value))

    async def set_mapping(self, region: str, mapping: ProductCategoryMappingDTO) -> None:
        """写入分类映射缓存，TTL 复用查询缓存配置，避免长期保存过期映射。"""

        if not self._settings.enabled:
            return

        try:
            client = await self._get_client()
            await client.setex(
                self._build_key(region, mapping.category_name),
                self._settings.product_search_cache_ttl_seconds,
                json.dumps(mapping.model_dump(exclude_none=True), ensure_ascii=False),
            )
        except Exception as exc:  # 缓存写入失败不影响接口返回。
            logger.warning("category_cache_set_failed error_type=%s", type(exc).__name__)

    async def _get_client(self) -> Any:
        """懒加载 Redis 客户端，避免未启用缓存时建立连接。"""

        if self._client is None:
            from redis.asyncio import Redis

            self._client = Redis.from_url(self._settings.url, decode_responses=True)
        return self._client

    def _build_key(self, region: str, category_name: str) -> str:
        """构造分类映射缓存 key，不包含密钥、token 或用户敏感凭据。"""

        return f"{CATEGORY_MAPPING_CACHE_PREFIX}:{region}:{category_name}"
