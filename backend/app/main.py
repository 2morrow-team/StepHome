# FastAPI 애플리케이션 진입점
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.plan import router as plan_router
from app.routers.replan import router as replan_router
from app.schemas.schemas import HealthResponse


app = FastAPI(title="StepHome API", version="v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(plan_router)
app.include_router(replan_router)


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "OK"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(item) for item in error.get("loc", [])),
            "reason": error.get("msg", "입력값이 올바르지 않습니다."),
        }
        for error in exc.errors()
    ]
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
async def value_error_handler(_, exc: ValueError) -> JSONResponse:
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
async def lookup_error_handler(_, exc: LookupError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "PLAN_NOT_FOUND",
                "message": str(exc),
            }
        },
    )
