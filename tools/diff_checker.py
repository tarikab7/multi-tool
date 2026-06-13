import difflib

async def run(params: dict):
    text1 = params.get("text1", "").strip()
    text2 = params.get("text2", "").strip()
    
    yield {"type": "log", "message": "Comparing text lines..."}
    
    try:
        t1_lines = text1.splitlines()
        t2_lines = text2.splitlines()
        
        diff = difflib.ndiff(t1_lines, t2_lines)
        found_diff = False
        
        for line in diff:
            if line.startswith("- ") or line.startswith("+ "):
                yield {"type": "found", "message": line}
                found_diff = True
                
        if not found_diff:
            yield {"type": "log", "message": "Text lines are completely identical."}
            
        yield {"type": "success", "message": "Line comparison finished."}
    except Exception as e:
        yield {"type": "error", "message": f"Comparison failed: {str(e)}"}
