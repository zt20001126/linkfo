import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.common.result import build_error_response
from app.core.config import get_settings
from app.exceptions.business_exception import BusinessException

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(BusinessException)
async def handle_business_exception(_, exc: BusinessException) -> JSONResponse:
    """业务异常统一转成前端约定的 JSON 响应，避免泄露内部实现细节。"""

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(code=exc.code, message=exc.message),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_, exc: RequestValidationError) -> JSONResponse:
    """请求校验失败统一返回安全提示，不把 Pydantic 原始错误结构直接暴露给前端。"""

    logger.info("request_validation_failed error_count=%s", len(exc.errors()))
    invalid_prompt = any(
        len(error.get("loc", ())) >= 2 and error.get("loc", ())[-1] == "prompt"
        for error in exc.errors()
    )
    if invalid_prompt:
        return JSONResponse(
            status_code=400,
            content=build_error_response(code="INVALID_PROMPT", message="请传入 prompt 字段"),
        )
    return JSONResponse(
        status_code=400,
        content=build_error_response(code="INVALID_REQUEST", message="请求参数不合法"),
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(_, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP 框架异常统一转成项目响应格式。"""

    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=build_error_response(code="NOT_FOUND", message="接口不存在"),
        )
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content=build_error_response(code="METHOD_NOT_ALLOWED", message="请求方法不允许"),
            headers=exc.headers,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(code="HTTP_ERROR", message="请求处理失败"),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def handle_unknown_exception(_, exc: Exception) -> JSONResponse:
    """未知异常只记录服务端日志，响应给前端安全错误信息。"""

    logger.exception("unexpected_backend_error error_type=%s", type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content=build_error_response(code="INTERNAL_ERROR", message="服务器内部错误"),
    )
