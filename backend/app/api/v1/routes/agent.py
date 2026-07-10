from fastapi import APIRouter, Depends

from app.common.result import ApiResponse, build_success_response
from app.schemas.product_search import (
    CapabilityTool,
    ProductCapabilitiesData,
    ProductSearchRequest,
)
from app.services.product_search_service import ProductSearchService, get_product_search_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/capabilities", response_model=ApiResponse)
async def get_capabilities() -> ApiResponse:
    """Agent 能力路由，声明当前后端已开放和规划中的工具。"""

    data = ProductCapabilitiesData(
        tools=[
            CapabilityTool(
                id="echotik_product_search",
                name="EchoTik 商品搜索",
                status="planned",
            )
        ]
    )
    return build_success_response(data=data)


@router.post("/product-search", response_model=ApiResponse)
async def search_products(
    request: ProductSearchRequest,
    service: ProductSearchService = Depends(get_product_search_service),
) -> ApiResponse:
    """选品搜索路由，负责请求绑定并委托业务服务。"""

    data = await service.search(request)
    return build_success_response(
        code="BACKEND_SKELETON_READY",
        message="后端基础框架已连通，EchoTik API 调用尚未实现",
        data=data,
    )
