from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.errors import ApiError
from app.api.routes import router


app = FastAPI(title="Legal Tech Document Service")
app.include_router(router)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": 5000},
    )
