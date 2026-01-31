import logging
import time

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.redis import init_redis_pool, close_redis_pool

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    load_dotenv() # Load environment variables from .env file
    logger.info("Starting GitHub Releases Store API")
    logger.info(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="GitHub Releases Store API",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.on_event("startup")
    async def startup():
        await init_redis_pool()
        # init_db is now handled by data-service

    @app.on_event("shutdown")
    async def shutdown():
        await close_redis_pool()

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Log all requests with timing information."""
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}ms")

        return response

    @app.middleware("http")
    async def universal_response_middleware(request: Request, call_next):
        """
        所有正常响应都将被包装在"通用响应"格式中
        {
            "code": 200,
            "message": "success",
            "data": ...
        }
        """
        response = await call_next(request)
        if (
            response.status_code == status.HTTP_200_OK
            and not isinstance(response, StreamingResponse)
        ):
            body = getattr(response, "body", None)
            if body is None:
                return response
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": status.HTTP_200_OK,
                    "message": "success",
                    "data": jsonable_encoder(body),
                },
            )
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP exception for {request.url.path}: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "error": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error for {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "request validation error",
                "error": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error for {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "internal server error",
                "error": str(exc),
            },
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
