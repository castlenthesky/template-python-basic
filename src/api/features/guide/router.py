from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import markdown
import os
from pathlib import Path
import aiofiles

guide_router = APIRouter()

DOCS_DIR = Path("docs")


async def _serve_markdown_file(file_name: str) -> HTMLResponse:
    """Helper function to serve a markdown file as HTML."""
    # Sanitize file name to prevent directory traversal
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    file_path = DOCS_DIR / f"{file_name}.md"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            md_text = await f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading file")
    
    # Convert markdown to HTML with extensions
    html = markdown.markdown(
        md_text,
        extensions=['codehilite', 'fenced_code', 'tables', 'toc']
    )
    
    # Enhanced HTML template with basic styling
    wrapped_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{file_name.title()} - Documentation</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                color: #333;
            }}
            code {{
                background: #f4f4f4;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-family: 'Monaco', 'Courier New', monospace;
            }}
            pre {{
                background: #f4f4f4;
                padding: 1rem;
                border-radius: 5px;
                overflow-x: auto;
            }}
            h1, h2, h3 {{ color: #2c3e50; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    return HTMLResponse(content=wrapped_html)


@guide_router.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the index documentation page."""
    return await _serve_markdown_file("index")


@guide_router.get("/{file_name}", response_class=HTMLResponse)
async def serve_doc(file_name: str):
    """Serve a specific documentation file."""
    return await _serve_markdown_file(file_name)
