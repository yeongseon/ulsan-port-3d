from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import ProblemDetail


class ProblemHTTPException(Exception):
    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        type_: str = "about:blank",
        instance: str | None = None,
    ) -> None:
        self.problem = ProblemDetail(
            type=type_, title=title, status=status, detail=detail, instance=instance
        )
        super().__init__(detail)


def build_problem(
    *,
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    instance: str | None = None,
) -> ProblemDetail:
    return ProblemDetail(type=type_, title=title, status=status, detail=detail, instance=instance)


async def problem_exception_handler(_: Request, exc: ProblemHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.problem.status,
        content=exc.problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    problem = build_problem(
        status=exc.status_code,
        title="HTTP Error",
        detail=str(exc.detail),
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    problem = build_problem(
        status=422,
        title="Validation Error",
        detail=str(exc),
        instance=str(request.url.path),
        type_="https://datatracker.ietf.org/doc/html/rfc7807",
    )
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )
