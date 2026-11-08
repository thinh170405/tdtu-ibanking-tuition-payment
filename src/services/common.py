from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorResponse(StrictModel):
    code: str
    message: str


def error(status: int, code: str, message: str, headers: dict | None = None):
    return JSONResponse(status_code=status, content={"code": code, "message": message}, headers=headers)


def install_error_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError):
        return error(400, "VALIDATION_ERROR", "Dữ liệu yêu cầu không hợp lệ.")

    @app.exception_handler(Exception)
    async def internal_error(_request: Request, _exc: Exception):
        return error(500, "INTERNAL_ERROR", "Hệ thống gặp lỗi. Vui lòng thử lại.")

    def contract_openapi():
        if app.openapi_schema is None:
            schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
            for operations in schema.get("paths", {}).values():
                for operation in operations.values():
                    if isinstance(operation, dict):
                        operation.get("responses", {}).pop("422", None)
            app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = contract_openapi
