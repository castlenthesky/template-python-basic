"""Controllers for Guide API endpoints."""

from fastapi.responses import FileResponse, HTMLResponse

from src.services.guide.service import DocumentService


async def handle_serve_document(service: DocumentService, path: str = "index") -> HTMLResponse:
    """Handle serving a markdown document as HTML."""
    return await service.serve_markdown_document(path)


async def handle_serve_asset(service: DocumentService, asset_path: str) -> FileResponse:
    """Handle serving a static asset file."""
    return await service.serve_static_asset(asset_path)