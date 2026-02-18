#!/usr/bin/env python3
"""
Convert Markdown paper report to HTML with LaTeX formula rendering (KaTeX).
Usage: python3 generate-html.py input.md output.html
"""

import sys
import re
import markdown

def protect_math(md_text):
    """Extract LaTeX blocks/inline before markdown processing, replace with placeholders."""
    placeholders = []
    
    # Display math: $$ ... $$ (multiline)
    def replace_display(m):
        idx = len(placeholders)
        placeholders.append(('display', m.group(1).strip()))
        return f'\n\nMATH_PLACEHOLDER_{idx}\n\n'
    
    md_text = re.sub(r'\$\$(.*?)\$\$', replace_display, md_text, flags=re.DOTALL)
    
    # Inline math: $ ... $ (but not $$)
    def replace_inline(m):
        idx = len(placeholders)
        placeholders.append(('inline', m.group(1)))
        return f'MATH_PLACEHOLDER_{idx}'
    
    md_text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', replace_inline, md_text)
    
    # \( ... \) inline
    def replace_paren(m):
        idx = len(placeholders)
        placeholders.append(('inline', m.group(1)))
        return f'MATH_PLACEHOLDER_{idx}'
    
    md_text = re.sub(r'\\\((.+?)\\\)', replace_paren, md_text)
    
    # \[ ... \] display
    def replace_bracket(m):
        idx = len(placeholders)
        placeholders.append(('display', m.group(1).strip()))
        return f'\n\nMATH_PLACEHOLDER_{idx}\n\n'
    
    md_text = re.sub(r'\\\[(.*?)\\\]', replace_bracket, md_text, flags=re.DOTALL)
    
    return md_text, placeholders

def restore_math(html_text, placeholders):
    """Restore LaTeX from placeholders into KaTeX-compatible HTML spans."""
    for idx, (kind, latex) in enumerate(placeholders):
        token = f'MATH_PLACEHOLDER_{idx}'
        # Escape HTML entities in latex that markdown might have mangled
        latex_clean = latex.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        if kind == 'display':
            replacement = f'<div class="katex-display">\\[{latex_clean}\\]</div>'
        else:
            replacement = f'<span class="katex-inline">\\({latex_clean}\\)</span>'
        html_text = html_text.replace(f'<p>{token}</p>', replacement)
        html_text = html_text.replace(token, replacement)
    return html_text

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<!-- KaTeX CSS & JS (CDN) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {{
        delimiters: [
            {{left: '\\\\[', right: '\\\\]', display: true}},
            {{left: '\\\\(', right: '\\\\)', display: false}},
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}}
        ],
        throwOnError: false
    }});"></script>
<style>
body {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px 30px;
    line-height: 1.8;
    color: #333;
    background: #fff;
}}
h1 {{ color: #1B3A5C; border-bottom: 2px solid #E67E22; padding-bottom: 8px; }}
h2 {{ color: #1B3A5C; margin-top: 2em; }}
h3 {{ color: #2c5282; }}
code {{
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
}}
pre {{
    background: #f8f8f8;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid #e0e0e0;
}}
blockquote {{
    border-left: 4px solid #E67E22;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #fdf6ec;
    color: #555;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}}
th {{
    background: #1B3A5C;
    color: white;
}}
tr:nth-child(even) {{ background: #f9f9f9; }}
img {{ max-width: 100%; height: auto; }}
.katex-display {{
    margin: 1.2em 0;
    overflow-x: auto;
    text-align: center;
}}
.katex {{ font-size: 1.1em; }}
a {{ color: #2563eb; }}
a:hover {{ color: #E67E22; }}
</style>
</head>
<body>
{content}
</body>
</html>"""

def md_to_html(md_text, title="Paper Report"):
    """Convert markdown with LaTeX to styled HTML with KaTeX rendering."""
    # Step 1: Protect math expressions
    protected_md, placeholders = protect_math(md_text)
    
    # Step 2: Convert markdown to HTML
    extensions = ['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']
    try:
        html_body = markdown.markdown(protected_md, extensions=extensions)
    except:
        html_body = markdown.markdown(protected_md, extensions=['tables'])
    
    # Step 3: Restore math expressions
    html_body = restore_math(html_body, placeholders)
    
    # Step 4: Wrap in template
    return HTML_TEMPLATE.format(title=title, content=html_body)

def extract_title(md_text):
    """Extract title from first # heading."""
    m = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "Paper Report"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 generate-html.py input.md output.html")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    title = extract_title(md_content)
    html = md_to_html(md_content, title)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated: {output_path} ({len(html)} bytes, {len(md_content)} md chars)")
