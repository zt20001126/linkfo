import os
from dataclasses import dataclass
from functools import lru_cache

from app.common.constants import (
    DEFAULT_DATABASE_URL,
    DEFAULT_ECHOTIK_BASE_URL,
    DEFAULT_ECHOTIK_CATEGORY_L1_PATH,
    DEFAULT_ECHOTIK_PRODUCT_LIST_PATH,
    DEFAULT_ECHOTIK_TIMEOUT_SECONDS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PRODUCT_SEARCH_CACHE_TTL_SECONDS,
    DEFAULT_REDIS_URL,
)


@dataclass(frozen=True)
class EchoTikSettings:
    """EchoTik 配置，影响后续商品服务真实 API 调用；敏感值只能来自环境变量。"""

    base_url: str
    product_list_path: str
    category_l1_path: str
    enable_real_api: bool
    timeout_seconds: float
    username: str
    password: str


@dataclass(frozen=True)
class DatabaseSettings:
    """数据库配置，影响查询记录和分类映射持久化；本地默认连接 Docker PostgreSQL。"""

    url: str
    enabled: bool


@dataclass(frozen=True)
class RedisSettings:
    """Redis 配置，影响商品查询和分类映射缓存；默认关闭，避免无 Redis 时阻塞开发。"""

    url: str
    enabled: bool
    product_search_cache_ttl_seconds: int


@dataclass(frozen=True)
class Settings:
    """应用运行配置，集中影响 FastAPI 启动、CORS 和外部 EchoTik 服务边界。"""

    app_name: str
    host: str
    port: int
    cors_allow_origins: list[str]
    cors_allow_methods: list[str]
    cors_allow_headers: list[str]
    echotik: EchoTikSettings
    database: DatabaseSettings
    redis: RedisSettings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """读取环境变量并返回不可变配置对象，避免业务层散落读取 process/env。"""

    return Settings(
        app_name="Linkfox Product Agent Backend",
        host=os.getenv("HOST", DEFAULT_HOST),
        port=int(os.getenv("PORT", str(DEFAULT_PORT))),
        cors_allow_origins=["*"],
        cors_allow_methods=["GET", "POST", "OPTIONS"],
        cors_allow_headers=["Content-Type", "Authorization"],
        echotik=EchoTikSettings(
            base_url=os.getenv("ECHOTIK_BASE_URL", DEFAULT_ECHOTIK_BASE_URL),
            product_list_path=os.getenv("ECHOTIK_PRODUCT_LIST_PATH", DEFAULT_ECHOTIK_PRODUCT_LIST_PATH),
            category_l1_path=os.getenv("ECHOTIK_CATEGORY_L1_PATH", DEFAULT_ECHOTIK_CATEGORY_L1_PATH),
            enable_real_api=_read_bool("ECHOTIK_ENABLE_REAL_API", False),
            timeout_seconds=float(os.getenv("ECHOTIK_TIMEOUT_SECONDS", str(DEFAULT_ECHOTIK_TIMEOUT_SECONDS))),
            username=os.getenv("ECHOTIK_USERNAME", ""),
            password=os.getenv("ECHOTIK_PASSWORD", ""),
        ),
        database=DatabaseSettings(
            url=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
            enabled=_read_bool("DATABASE_ENABLED", False),
        ),
        redis=RedisSettings(
            url=os.getenv("REDIS_URL", DEFAULT_REDIS_URL),
            enabled=_read_bool("REDIS_ENABLED", False),
            product_search_cache_ttl_seconds=int(
                os.getenv(
                    "PRODUCT_SEARCH_CACHE_TTL_SECONDS",
                    str(DEFAULT_PRODUCT_SEARCH_CACHE_TTL_SECONDS),
                )
            ),
        ),
    )


def _read_bool(name: str, fallback: bool) -> bool:
    """读取布尔环境变量，支持常见 true/false 写法，避免业务代码重复解析。"""

    raw_value = os.getenv(name)
    if raw_value is None:
        return fallback
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}
