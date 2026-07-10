from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
