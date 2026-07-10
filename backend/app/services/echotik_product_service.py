import base64
import logging
from typing import Any

import httpx

from app.core.config import EchoTikSettings, get_settings
from app.exceptions.business_exception import BusinessException
from app.schemas.product_search import EchoTikProductListParams, EchoTikProductSearchResult

logger = logging.getLogger(__name__)

SENSITIVE_RESPONSE_KEYS = {"authorization", "token", "cookie", "password", "secret", "signature", "sign"}


class EchoTikProductService:
    """EchoTik 商品服务，负责真实 API 调用、鉴权、超时和安全错误转换。"""

    def __init__(self, settings: EchoTikSettings | None = None) -> None:
        self._settings = settings or get_settings().echotik

    async def search_products(self, params: EchoTikProductListParams) -> EchoTikProductSearchResult:
        """搜索 EchoTik 商品。

        Step 1: 接收已经标准化的 EchoTik 商品查询参数。
        Step 2: 未启用真实 API 时不发起外部请求，返回空商品列表。
        Step 3: 启用真实 API 后使用 Basic Auth 调用 EchoTik 商品列表接口。
        Step 4: 将第三方超时、限流和失败响应转换为安全业务异常。
        """

        if not self._settings.enable_real_api:
            return EchoTikProductSearchResult(implemented=False, params=params, items=[])

        if not self._settings.username or not self._settings.password:
            raise BusinessException(
                code="ECHOTIK_CONFIG_MISSING",
                message="EchoTik 鉴权配置缺失，请先配置用户名和密码",
                status_code=500,
            )

        url = self._build_product_list_url()
        try:
            async with httpx.AsyncClient(timeout=self._settings.timeout_seconds) as client:
                response = await client.get(
                    url,
                    params=params.model_dump(exclude_none=True),
                    headers=self._build_auth_headers(),
                )
        except httpx.TimeoutException as exc:
            logger.warning("echotik_product_list_timeout error_type=%s", type(exc).__name__)
            raise BusinessException(
                code="ECHOTIK_TIMEOUT",
                message="EchoTik 商品查询超时，请稍后重试",
                status_code=504,
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("echotik_product_list_http_error error_type=%s", type(exc).__name__)
            raise BusinessException(
                code="ECHOTIK_REQUEST_FAILED",
                message="EchoTik 商品查询失败，请稍后重试",
                status_code=502,
            ) from exc

        if response.status_code == 429:
            raise BusinessException(
                code="ECHOTIK_RATE_LIMITED",
                message="EchoTik 查询过于频繁，请稍后重试",
                status_code=429,
            )
        if response.status_code >= 400:
            logger.warning("echotik_product_list_bad_status status_code=%s", response.status_code)
            raise BusinessException(
                code="ECHOTIK_REQUEST_FAILED",
                message="EchoTik 商品查询失败，请稍后重试",
                status_code=502,
            )

        payload = self._read_json_payload(response)
        items = self._extract_items(payload)
        return EchoTikProductSearchResult(implemented=True, params=params, items=items)

    def _build_product_list_url(self) -> str:
        """构造 EchoTik 商品列表 URL，避免业务代码散落拼接规则。"""

        base_url = self._settings.base_url.rstrip("/")
        path = self._settings.product_list_path if self._settings.product_list_path.startswith("/") else f"/{self._settings.product_list_path}"
        return f"{base_url}{path}"

    def _build_auth_headers(self) -> dict[str, str]:
        """构造 Basic Auth 头，日志和响应中禁止输出该值。"""

        raw_credential = f"{self._settings.username}:{self._settings.password}"
        token = base64.b64encode(raw_credential.encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}"}

    def _read_json_payload(self, response: httpx.Response) -> dict[str, Any]:
        """读取第三方 JSON 响应，格式异常时转换为安全业务错误。"""

        try:
            payload = response.json()
        except ValueError as exc:
            logger.warning("echotik_product_list_invalid_json status_code=%s", response.status_code)
            raise BusinessException(
                code="ECHOTIK_REQUEST_FAILED",
                message="EchoTik 商品查询失败，请稍后重试",
                status_code=502,
            ) from exc

        if not isinstance(payload, dict):
            raise BusinessException(
                code="ECHOTIK_REQUEST_FAILED",
                message="EchoTik 商品查询失败，请稍后重试",
                status_code=502,
            )
        return payload

    def _extract_items(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """从常见商品列表响应位置提取商品数组，并移除明显敏感字段。"""

        candidates = [
            payload.get("data"),
            payload.get("items"),
            payload.get("list"),
            payload.get("records"),
        ]
        data = payload.get("data")
        if isinstance(data, dict):
            candidates.extend([data.get("items"), data.get("list"), data.get("records")])

        items = next((candidate for candidate in candidates if isinstance(candidate, list)), [])
        return [self._sanitize_item(item) for item in items if isinstance(item, dict)]

    def _sanitize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """脱敏商品字段，避免 token、cookie、签名等第三方敏感信息透传到前端。"""

        sanitized: dict[str, Any] = {}
        for key, value in item.items():
            if key.lower() in SENSITIVE_RESPONSE_KEYS:
                continue
            sanitized[key] = value
        return sanitized
