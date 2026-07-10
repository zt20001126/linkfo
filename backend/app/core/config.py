import os
from dataclasses import dataclass
from functools import lru_cache

from app.common.constants import DEFAULT_ECHOTIK_BASE_URL, DEFAULT_HOST, DEFAULT_PORT


@dataclass(frozen=True)
class EchoTikSettings:
    """EchoTik 配置，影响后续商品服务真实 API 调用；敏感值只能来自环境变量。"""

    base_url: str
    username: str
    password: str


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
            username=os.getenv("ECHOTIK_USERNAME", ""),
            password=os.getenv("ECHOTIK_PASSWORD", ""),
        ),
    )
