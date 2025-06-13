"""
Custom exception handlers for the Ludora backend API.
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Adjust level as needed

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for FastAPI's HTTPException.
    Standardizes the error response format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "type": "HTTPException"},
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Custom handler for unhandled exceptions.
    Logs the error and returns a generic 500 response.
    """
    logger.error(f"Unhandled exception for request {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected internal server error occurred.", "type": "InternalServerError"},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic's RequestValidationError.
    Provides a more detailed error response for validation failures.
    """
    # Log the validation errors for debugging if necessary
    # logger.warning(f"Request validation failed for {request.method} {request.url}: {exc.errors()}")

    # Example of a more customized error structure, could also use exc.errors() directly
    # error_details = []
    # for error in exc.errors():
    #     field = " -> ".join(str(loc) for loc in error['loc']) if error['loc'] else 'general'
    #     message = error['msg']
    #     error_type = error['type']
    #     error_details.append({"field": field, "message": message, "type": error_type})

    return JSONResponse(
        status_code=422, # HTTP_422_UNPROCESSABLE_ENTITY
        content={
            "message": "Request validation failed. Please check your input.",
            "type": "RequestValidationError",
            "details": exc.errors() # FastAPI's default error structure is quite good and detailed.
        }
    )
