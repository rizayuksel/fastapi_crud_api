import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AppException

# Just a basic logger to track the mess
logger = logging.getLogger("app")


def add_exception_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        # Catch our custom exceptions and stay calm
        logger.error(f"Application error: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # The 'oh no, everything is on fire' handler
        logger.critical("Unexpected error occurred", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",  # ✅ Standart
                    "message": "An unexpected error occurred",  # ✅ Standart
                },
            },
        )
