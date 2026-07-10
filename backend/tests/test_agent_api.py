import asyncio

from fastapi.testclient import TestClient
import pytest

from app.core.config import EchoTikSettings
from app.exceptions.business_exception import BusinessException
from app.main import app
from app.schemas.product_search import EchoTikProductListParams
from app.services.echotik_product_service import EchoTikProductService

client = TestClient(app)


def test_root_serves_frontend_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "promptInput" in response.text


def test_frontend_src_static_files_are_served() -> None:
    response = client.get("/src/scripts/product-agent.js")

    assert response.status_code == 200
    assert "ProductAgentPromptParser" in response.text


def test_health_returns_success() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": "SUCCESS",
        "message": None,
        "data": {
            "service": "linkfox-product-agent-backend",
            "status": "ok",
        },
    }


def test_capabilities_returns_planned_echotik_tool() -> None:
    response = client.get("/api/agent/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "SUCCESS"
    assert payload["data"]["tools"][0]["id"] == "echotik_product_search"
    assert payload["data"]["tools"][0]["status"] == "planned"


def test_product_search_returns_parsed_echotik_params() -> None:
    response = client.post(
        "/api/agent/product-search",
        json={
            "prompt": "@EchoTik-TikTok商品搜索 在 TikTok Shop，美国站，商品关键词 公路自行车，商品分类 运动与户外，按 总销量 排序，排序方式 降序，第 2 页，每页 10 条。"
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "BACKEND_SKELETON_READY"
    assert payload["data"]["query"]["platform"] == "TikTok Shop"
    assert payload["data"]["query"]["region"] == "US"
    assert payload["data"]["query"]["keyword"] == "公路自行车"
    assert payload["data"]["query"]["categoryName"] == "运动与户外"
    assert payload["data"]["echotikParams"] == {
        "region": "US",
        "page_num": 2,
        "page_size": 10,
        "product_sort_field": 1,
        "sort_type": 1,
    }
    assert payload["data"]["items"] == []


def test_product_search_clamps_page_size_to_echotik_limit() -> None:
    response = client.post(
        "/api/agent/product-search",
        json={
            "prompt": "@EchoTik-TikTok商品搜索 在 TikTok Shop，美国站，商品关键词 公路自行车，商品分类 运动与户外，按 总销量 排序，排序方式 降序，第 200000 页，每页 99 条。"
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["query"]["page"] == 100000
    assert payload["data"]["query"]["pageSize"] == 10
    assert payload["data"]["echotikParams"]["page_num"] == 100000
    assert payload["data"]["echotikParams"]["page_size"] == 10


def test_product_search_does_not_send_keyword_to_echotik_params() -> None:
    response = client.post(
        "/api/agent/product-search",
        json={
            "prompt": "@EchoTik-TikTok商品搜索 在 TikTok Shop，美国站，商品关键词 公路自行车，按 总销量 排序，排序方式 降序，第 1 页，每页 3 条。"
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["query"]["keyword"] == "公路自行车"
    assert "keyword" not in payload["data"]["echotikParams"]


def test_product_search_rejects_blank_prompt() -> None:
    response = client.post("/api/agent/product-search", json={"prompt": "   "})

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PROMPT"


def test_unknown_api_returns_not_found_code() -> None:
    response = client.get("/api/unknown")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_wrong_method_returns_method_not_allowed_code() -> None:
    response = client.get("/api/agent/product-search")

    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"


def test_echotik_service_requires_credentials_when_real_api_enabled() -> None:
    service = EchoTikProductService(
        EchoTikSettings(
            base_url="https://open.echotik.live",
            product_list_path="/api/v3/echotik/product/list",
            category_l1_path="/api/v3/echotik/category/l1",
            enable_real_api=True,
            timeout_seconds=1,
            username="",
            password="",
        )
    )

    with pytest.raises(BusinessException) as exc_info:
        asyncio.run(
            service.search_products(
                EchoTikProductListParams(
                    region="US",
                    page_num=1,
                    page_size=10,
                    product_sort_field=1,
                    sort_type=1,
                )
            )
        )

    assert exc_info.value.code == "ECHOTIK_CONFIG_MISSING"
