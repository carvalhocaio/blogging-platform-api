from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from blogging_platform_api.domain.errors import PostNotFoundError
from blogging_platform_api.web.schemas import ErrorDetail, ErrorResponse

BODY_LOCATIONS = frozenset({"body", "query", "path"})


def to_field(location: tuple[int | str, ...]) -> str | None:
    parts = [str(part) for part in location if str(part) not in BODY_LOCATIONS]
    return ".".join(parts) if parts else None


def error_response(
    status_code: int, message: str, errors: list[ErrorDetail] | None = None
) -> JSONResponse:
    payload = ErrorResponse(message=message, errors=errors or [])
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def handle_validation_error(
    _request: Request, exception: Exception
) -> JSONResponse:
    assert isinstance(exception, RequestValidationError)
    details = [
        ErrorDetail(field=to_field(error["loc"]), message=error["msg"])
        for error in exception.errors()
    ]
    return error_response(status.HTTP_400_BAD_REQUEST, "validation failed", details)


async def handle_post_not_found(
    _request: Request, exception: Exception
) -> JSONResponse:
    assert isinstance(exception, PostNotFoundError)
    return error_response(status.HTTP_404_NOT_FOUND, str(exception))


def register_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(PostNotFoundError, handle_post_not_found)
