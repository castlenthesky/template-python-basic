from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import markdown
import os

docs_router = APIRouter()

DOCS_DIR = "docs"

@docs_router.get("/{file_name}", response_class=HTMLResponse)
async def serve_doc(file_name: str):
    file_path = os.path.join(DOCS_DIR, f"{file_name}.md")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "r") as f:
        md_text = f.read()
    html = markdown.markdown(md_text)
    # Optional: Wrap in a template for styling
    wrapped_html = f"<html><body>{html}</body></html>"
    return HTMLResponse(content=wrapped_html)