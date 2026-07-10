from fastapi import APIRouter

from app.common.result import ApiResponse, build_success_response
from app.schemas.product_search import HealthData

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse)
async def get_health() -> ApiResponse:
    """健康检查路由，仅返回服务存活状态。"""

    data = HealthData(service="linkfox-product-agent-backend", status="ok")
    return build_success_response(data=data)
