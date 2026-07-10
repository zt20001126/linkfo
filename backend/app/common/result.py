from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一接口响应结构，用于保持前后端约定的 code/message/data 格式。"""

    code: str = Field(..., description="业务响应码，前端据此判断请求结果")
    message: str | None = Field(default=None, description="面向用户的安全提示信息")
    data: Any = Field(default=None, description="接口业务数据载荷")


def build_success_response(
    data: Any,
    code: str = "SUCCESS",
    message: str | None = None,
) -> ApiResponse:
    """构造成功响应，集中维护后端统一返回格式。"""

    return ApiResponse(code=code, message=message, data=data)


def build_error_response(code: str, message: str) -> dict[str, Any]:
    """构造错误响应字典，异常处理器直接返回安全信息。"""

    return {"code": code, "message": message}
