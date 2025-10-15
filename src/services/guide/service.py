"""Document service for business logic operations."""

import logging
import mimetypes
import re
from pathlib import Path
from typing import List, Optional, Tuple

import aiofiles
import markdown
from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from .exceptions import DocumentNotFoundError, InvalidPathError
from .models import DocumentMetadata, TemplateData
from .templates import generate_html_template

logger = logging.getLogger(__name__)


class DocumentService:
    """Document service with business logic methods."""

    def __init__(self, docs_dir: str = "docs"):
        """Initialize document service with docs directory."""
        self.docs_dir = Path(docs_dir)
        if not self.docs_dir.exists():
            logger.warning(f"Documentation directory {docs_dir} does not exist")

    async def serve_markdown_document(self, path: str) -> HTMLResponse:
        """Serve a markdown document as HTML with proper styling and navigation."""
        try:
            # Validate and sanitize the path
            safe_path = self._validate_path(path)
            
            # Get document metadata
            metadata = self._get_document_metadata(safe_path)
            
            # Read and process markdown content
            markdown_content = await self._read_markdown_file(safe_path)
            processed_content = self._process_relative_links(markdown_content, safe_path)
            
            # Convert to HTML
            html_content = self._markdown_to_html(processed_content)
            
            # Generate complete HTML page
            full_html = generate_html_template(
                title=metadata.title,
                content=html_content,
                breadcrumbs=metadata.breadcrumbs
            )
            
            return HTMLResponse(content=full_html)
            
        except DocumentNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except InvalidPathError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error serving document {path}: {e}")
            raise HTTPException(status_code=500, detail="Error processing document")

    async def serve_static_asset(self, asset_path: str) -> FileResponse:
        """Serve a static asset file with proper headers."""
        try:
            # Validate and sanitize the asset path
            safe_path = self._validate_asset_path(asset_path)
            
            # Check if file exists
            full_path = self.docs_dir / "assets" / safe_path
            if not full_path.exists() or not full_path.is_file():
                raise HTTPException(status_code=404, detail="Asset not found")
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(full_path))
            if mime_type is None:
                mime_type = "application/octet-stream"
            
            return FileResponse(
                path=str(full_path),
                media_type=mime_type,
                headers={
                    "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                    "X-Content-Type-Options": "nosniff"
                }
            )
            
        except Exception as e:
            logger.error(f"Error serving asset {asset_path}: {e}")
            raise HTTPException(status_code=500, detail="Error serving asset")

    def _validate_path(self, path: str) -> str:
        """Validate and sanitize a document path."""
        if not path:
            return "index"
        
        # Remove leading/trailing slashes and normalize
        clean_path = path.strip("/")
        
        # Check for directory traversal attempts
        if ".." in clean_path or any(char in clean_path for char in ["<", ">", "|", ":", "*", "?"]):
            raise InvalidPathError(f"Invalid characters in path: {path}")
        
        # Ensure path doesn't try to escape docs directory
        try:
            resolved_path = (self.docs_dir / clean_path).resolve()
            if not str(resolved_path).startswith(str(self.docs_dir.resolve())):
                raise InvalidPathError(f"Path attempts to escape docs directory: {path}")
        except Exception:
            raise InvalidPathError(f"Invalid path: {path}")
        
        return clean_path

    def _validate_asset_path(self, asset_path: str) -> str:
        """Validate and sanitize an asset path."""
        if not asset_path:
            raise InvalidPathError("Asset path cannot be empty")
        
        # Remove leading/trailing slashes
        clean_path = asset_path.strip("/")
        
        # Check for directory traversal and invalid characters
        if ".." in clean_path or any(char in clean_path for char in ["<", ">", "|", ":", "*", "?"]):
            raise InvalidPathError(f"Invalid characters in asset path: {asset_path}")
        
        return clean_path

    def _get_document_metadata(self, path: str) -> DocumentMetadata:
        """Generate metadata for a document based on its path."""
        path_parts = path.split("/") if path != "index" else ["index"]
        
        # Generate breadcrumbs
        breadcrumbs = ["Home"]
        if path != "index":
            breadcrumbs.extend([part.replace("-", " ").title() for part in path_parts[:-1]])
            breadcrumbs.append(path_parts[-1].replace("-", " ").title())
        
        # Generate title
        if path == "index":
            title = "Documentation Home"
        else:
            title = path_parts[-1].replace("-", " ").title()
        
        return DocumentMetadata(
            title=title,
            path=path,
            breadcrumbs=breadcrumbs
        )

    async def _read_markdown_file(self, path: str) -> str:
        """Read markdown file content."""
        # Try exact path first, then with .md extension
        possible_paths = [
            self.docs_dir / f"{path}.md",
            self.docs_dir / path / "index.md",
        ]
        
        for file_path in possible_paths:
            if file_path.exists() and file_path.is_file():
                try:
                    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                        return await f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue
        
        raise DocumentNotFoundError(f"Document not found: {path}")

    def _process_relative_links(self, markdown_content: str, current_path: str) -> str:
        """Process relative links in markdown content to absolute URLs."""
        # Pattern to match markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Skip if already absolute URL or anchor
            if url.startswith(('http://', 'https://', '#', '/')):
                return match.group(0)
            
            # Handle relative paths
            if url.startswith('../'):
                # Go up one level from current path
                current_parts = current_path.split('/')[:-1] if current_path != "index" else []
                relative_url = url[3:]  # Remove ../
                new_path = '/'.join(current_parts + [relative_url]) if current_parts else relative_url
            else:
                # Same level or down
                current_dir = '/'.join(current_path.split('/')[:-1]) if '/' in current_path else ''
                new_path = f"{current_dir}/{url}" if current_dir else url
            
            # Remove .md extension for clean URLs
            if new_path.endswith('.md'):
                new_path = new_path[:-3]
            
            return f'[{text}](/guide/{new_path})'
        
        # Pattern to match markdown images: ![alt](url)
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            url = match.group(2)
            
            # Skip if already absolute URL
            if url.startswith(('http://', 'https://', '/')):
                return match.group(0)
            
            # Convert relative asset paths to absolute
            if url.startswith('assets/'):
                return f'![{alt_text}](/guide/{url})'
            elif not url.startswith('../'):
                # Assume it's an asset if it has an image extension
                if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']):
                    return f'![{alt_text}](/guide/assets/{url})'
            
            return match.group(0)
        
        # Apply both replacements
        processed = re.sub(link_pattern, replace_link, markdown_content)
        processed = re.sub(img_pattern, replace_image, processed)
        
        return processed

    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to HTML with extensions."""
        return markdown.markdown(
            markdown_content,
            extensions=[
                'codehilite',
                'fenced_code', 
                'tables',
                'toc',
                'attr_list',
                'def_list'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False  # Use CSS classes only
                }
            }
        )