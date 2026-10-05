"""统一异常处理：所有异常返回 {code, message} 友好结构，禁止泄露 Key / 堆栈。"""
from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """业务异常：携带 code 与 message。"""

    def __init__(self, message: str, code: int = 400) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.code, content={"code": exc.code, "message": exc.message})


async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数校验失败", "detail": exc.errors()},
    )


async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
    # 生产环境不暴露内部错误细节
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误，请稍后重试"})
