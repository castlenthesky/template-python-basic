"""HTML templates for document rendering."""

from typing import List


def generate_html_template(
    title: str,
    content: str, 
    breadcrumbs: List[str],
    base_url: str = "/guide"
) -> str:
    """Generate complete HTML document with styling and navigation."""
    
    breadcrumb_html = _generate_breadcrumb_html(breadcrumbs, base_url)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Documentation</title>
    <style>
        {_get_css_styles()}
    </style>
</head>
<body>
    <nav class="breadcrumb">
        {breadcrumb_html}
    </nav>
    <main class="content">
        {content}
    </main>
</body>
</html>"""


def _generate_breadcrumb_html(breadcrumbs: List[str], base_url: str) -> str:
    """Generate breadcrumb navigation HTML."""
    if not breadcrumbs:
        return ""
    
    crumbs = []
    current_path = base_url
    
    for i, crumb in enumerate(breadcrumbs):
        if i == len(breadcrumbs) - 1:
            # Current page - not a link
            crumbs.append(f'<span class="breadcrumb-current">{crumb}</span>')
        else:
            if i == 0:
                # Home link
                crumbs.append(f'<a href="{base_url}/">{crumb}</a>')
            else:
                # Build path for intermediate crumbs
                current_path += f"/{breadcrumbs[i]}"
                crumbs.append(f'<a href="{current_path}">{crumb}</a>')
    
    return ' / '.join(crumbs)


def _get_css_styles() -> str:
    """Get CSS styles for document rendering."""
    return """
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
            color: #333;
            background-color: #fff;
        }
        
        .breadcrumb {
            padding: 1rem 0;
            border-bottom: 1px solid #e1e5e9;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }
        
        .breadcrumb a {
            color: #0366d6;
            text-decoration: none;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        .breadcrumb-current {
            color: #586069;
            font-weight: 500;
        }
        
        .content {
            min-height: 400px;
        }
        
        h1, h2, h3, h4, h5, h6 { 
            color: #24292e;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        h1 { 
            font-size: 2rem;
            border-bottom: 1px solid #e1e5e9;
            padding-bottom: 0.3rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.25rem;
        }
        
        p {
            margin-bottom: 1rem;
        }
        
        code {
            background: #f6f8fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.9rem;
        }
        
        pre {
            background: #f6f8fa;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        pre code {
            background: none;
            padding: 0;
            font-size: 0.85rem;
        }
        
        a { 
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover { 
            text-decoration: underline;
        }
        
        img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        
        th, td {
            border: 1px solid #d0d7de;
            padding: 0.75rem;
            text-align: left;
        }
        
        th {
            background-color: #f6f8fa;
            font-weight: 600;
        }
        
        blockquote {
            border-left: 4px solid #d0d7de;
            padding: 0 1rem;
            margin: 1rem 0;
            color: #656d76;
        }
        
        ul, ol {
            padding-left: 2rem;
            margin: 1rem 0;
        }
        
        li {
            margin-bottom: 0.5rem;
        }
    """