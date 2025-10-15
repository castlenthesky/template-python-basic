"""Error handling middleware for the API."""

import logging
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.services.shared.exceptions import DuplicateError, NotFoundError

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Application-specific error code
        details: Additional error details
        
    Returns:
        JSONResponse with error details
    """
    content = {
        "error": {
            "message": message,
            "status_code": status_code,
        }
    }
    
    if error_code:
        content["error"]["code"] = error_code
        
    if details:
        content["error"]["details"] = details
        
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def handle_application_exceptions(request: Request, call_next):
    """
    Middleware to handle application-level exceptions.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/endpoint in the chain
        
    Returns:
        Response or error response
    """
    try:
        response = await call_next(request)
        return response
        
    except NotFoundError as e:
        logger.info(f"Not found error on {request.method} {request.url}: {str(e)}")
        return create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=str(e),
            error_code="RESOURCE_NOT_FOUND"
        )
        
    except DuplicateError as e:
        logger.info(f"Duplicate error on {request.method} {request.url}: {str(e)}")
        return create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            message=str(e),
            error_code="DUPLICATE_RESOURCE"
        )
        
    except IntegrityError as e:
        logger.warning(f"Database integrity error on {request.method} {request.url}: {str(e)}")
        return create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Data integrity constraint violated",
            error_code="INTEGRITY_ERROR"
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error on {request.method} {request.url}: {str(e)}")
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="A database error occurred",
            error_code="DATABASE_ERROR"
        )
        
    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions to be handled by FastAPI
        raise e
        
    except Exception as e:
        logger.error(f"Unexpected error on {request.method} {request.url}: {str(e)}", exc_info=True)
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR"
        )


def configure_error_handling(app):
    """
    Configure error handling middleware for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.middleware("http")(handle_application_exceptions)
    logger.info("Error handling middleware configured")