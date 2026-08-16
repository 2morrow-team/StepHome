# FastAPI 애플리케이션 진입점

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.plan import router as plan_router
from app.routers.replan import router as replan_router
from app.schemas.schemas import HealthResponse


app = FastAPI(
    title="StepHome API",
    description="StepHome Backend API",
    version="1.0.0",
)


# Frontend 개발 서버와의 로컬 통신 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Router 등록
app.include_router(plan_router)
app.include_router(replan_router)


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
)
def health() -> dict[str, str]:
    """Backend 서버 상태 확인."""
    return {"status": "OK"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Pydantic / FastAPI Request Validation 오류를
    Frontend 공통 Error Contract로 변환한다.

    FastAPI 내부 경로의 `body` prefix는 제거한다.

    예:
    body.user.age
    -> user.age
    """

    details = []

    for error in exc.errors():
        location = list(error.get("loc", []))

        # FastAPI 내부 prefix 제거
        if location and location[0] == "body":
            location = location[1:]

        field = ".".join(
            str(item)
            for item in location
        )

        details.append(
            {
                "field": field,
                "reason": error.get(
                    "msg",
                    "입력값이 올바르지 않습니다.",
                ),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": "입력값을 확인해주세요.",
                "details": details,
            }
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(
    _,
    exc: ValueError,
) -> JSONResponse:
    """
    서비스/Diagnosis 등에서 발생한
    사용자 입력 관련 ValueError 처리.
    """

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(LookupError)
async def lookup_error_handler(
    _,
    exc: LookupError,
) -> JSONResponse:
    """기존 Plan / User / Target 등을 찾지 못한 경우."""

    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "PLAN_NOT_FOUND",
                "message": str(exc),
            }
        },
    )
    