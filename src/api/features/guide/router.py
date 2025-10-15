"""FastAPI router for Guide API endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, HTMLResponse

from src.api.dependencies import get_document_service
from src.services.guide.service import DocumentService
from .controller import handle_serve_asset, handle_serve_document

guide_router = APIRouter()


@guide_router.get("/", response_class=HTMLResponse)
async def serve_index(
    service: DocumentService = Depends(get_document_service)
) -> HTMLResponse:
    """Serve the index documentation page."""
    return await handle_serve_document(service)


@guide_router.get("/assets/{asset_path:path}", response_class=FileResponse)
async def serve_asset(
    asset_path: str,
    service: DocumentService = Depends(get_document_service)
) -> FileResponse:
    """Serve static assets (images, CSS, JS, etc.)."""
    return await handle_serve_asset(service, asset_path)


@guide_router.get("/{path:path}", response_class=HTMLResponse)
async def serve_doc(
    path: str,
    service: DocumentService = Depends(get_document_service)
) -> HTMLResponse:
    """Serve a documentation file with nested path support."""
    return await handle_serve_document(service, path)
