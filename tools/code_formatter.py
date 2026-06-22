import json
import xml.dom.minidom
import asyncio
from bs4 import BeautifulSoup

def format_json(code, indent):
    parsed = json.loads(code)
    return json.dumps(parsed, indent=indent)

def format_xml(code, indent):
    
    soup = BeautifulSoup(code, 'html.parser')
    return soup.prettify()

def format_css(code, indent):
    
    lines = []
    indent_str = " " * indent
    
    code = code.replace("\n", "").replace("\r", "")
    parts = code.split("}")
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        subparts = part.split("{")
        selector = subparts[0].strip()
        body = subparts[1].strip() if len(subparts) > 1 else ""
        
        lines.append(f"{selector} {{")
        rules = body.split(";")
        for rule in rules:
            rule = rule.strip()
            if rule:
                lines.append(f"{indent_str}{rule};")
        lines.append("}\n")
        
    return "\n".join(lines)

def format_sql(code):
    
    keywords = ("SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", 
                "INNER JOIN", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", 
                "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM", "AND", "OR")
    
    code = " ".join(code.split()) 
    for kw in keywords:
        
        
        code = re.sub(rf'\b{kw}\b', f"\n{kw}", code, flags=re.IGNORECASE)
    
    return code.strip()

async def run(params: dict):
    lang = params.get("lang", "json").lower()
    indent_size_str = params.get("indent_size", "4").strip()
    raw_code = params.get("raw_code", "").strip()

    if not raw_code:
        yield {"type": "error", "message": "Raw code content is required."}
        return

    try:
        indent = int(indent_size_str)
    except ValueError:
        yield {"type": "error", "message": "Indentation size must be an integer."}
        return

    yield {"type": "log", "message": f"Formatting {lang.upper()} document..."}

    try:
        formatted = ""
        if lang == "json":
            formatted = await asyncio.to_thread(format_json, raw_code, indent)
        elif lang == "xml":
            formatted = await asyncio.to_thread(format_xml, raw_code, indent)
        elif lang == "css":
            formatted = await asyncio.to_thread(format_css, raw_code, indent)
        elif lang == "sql":
            import re  
            formatted = await asyncio.to_thread(format_sql, raw_code)
        else:
            yield {"type": "error", "message": f"Unsupported language: {lang}"}
            return

        yield {"type": "progress", "percent": 100.0}
        yield {"type": "log", "message": "\nFormatted Output:\n" + "="*40 + "\n" + formatted + "\n" + "="*40}
        yield {"type": "success", "message": f"Document formatted successfully."}

    except Exception as e:
        yield {"type": "error", "message": f"Formatting failed: {str(e)}"}
