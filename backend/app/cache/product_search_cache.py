import hashlib
import json
import logging
from typing import Any

from app.common.constants import PRODUCT_SEARCH_CACHE_PREFIX
from app.core.config import RedisSettings
from app.schemas.product_search import EchoTikProductListParams, EchoTikProductSearchResult

logger = logging.getLogger(__name__)


class ProductSearchCache:
    """商品搜索缓存，用于缓存短期重复 EchoTik 查询结果。"""

    def __init__(self, settings: RedisSettings) -> None:
        self._settings = settings
        self._client: Any | None = None

    async def get_result(self, params: EchoTikProductListParams) -> EchoTikProductSearchResult | None:
        """读取商品搜索缓存，Redis 未启用或异常时返回未命中。"""

        if not self._settings.enabled:
            return None

        try:
            client = await self._get_client()
            raw_value = await client.get(self._build_key(params))
        except Exception as exc:  # 缓存失败不能阻断 EchoTik 主链路。
            logger.warning("product_search_cache_get_failed error_type=%s", type(exc).__name__)
            return None

        if raw_value is None:
            return None

        payload = json.loads(raw_value)
        return EchoTikProductSearchResult(implemented=True, params=params, items=payload.get("items", []))

    async def set_result(self, params: EchoTikProductListParams, result: EchoTikProductSearchResult) -> None:
        """写入商品搜索缓存，只保存商品列表和已脱敏参数，不保存鉴权信息。"""

        if not self._settings.enabled or not result.implemented:
            return

        try:
            client = await self._get_client()
            await client.setex(
                self._build_key(params),
                self._settings.product_search_cache_ttl_seconds,
                json.dumps({"items": result.items}, ensure_ascii=False),
            )
        except Exception as exc:  # 缓存写入失败不影响接口返回。
            logger.warning("product_search_cache_set_failed error_type=%s", type(exc).__name__)

    async def _get_client(self) -> Any:
        """懒加载 Redis 客户端，避免未启用缓存时建立连接。"""

        if self._client is None:
            from redis.asyncio import Redis

            self._client = Redis.from_url(self._settings.url, decode_responses=True)
        return self._client

    def _build_key(self, params: EchoTikProductListParams) -> str:
        """构造稳定缓存 key，只基于公开查询参数，不包含密钥、token 或 cookie。"""

        params_json = json.dumps(params.model_dump(exclude_none=True), sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(params_json.encode("utf-8")).hexdigest()
        return f"{PRODUCT_SEARCH_CACHE_PREFIX}:{digest}"
