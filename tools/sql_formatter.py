import asyncio
from tools.utils import yield_log, yield_success, yield_error, ToolEvent

async def run(params: dict):
    sql = params.get("sql", "").strip()
    if not sql:
        yield yield_error("SQL query string is required.")
        return
        
    yield yield_log("Running syntax formatter on SQL statement...")
    await asyncio.sleep(0.5)
    
    try:
        # Simple SQL formatting logic using string splitting
        keywords = ["SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "AND", "OR", "GROUP BY", "ORDER BY", "LIMIT", "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM"]
        
        # Clean spacing
        sql_clean = " ".join(sql.split())
        
        # Replace keywords with newlines
        formatted = sql_clean
        for kw in keywords:
            formatted = formatted.replace(f" {kw} ", f"\n{kw} ")
            formatted = formatted.replace(f" {kw.lower()} ", f"\n{kw} ")
            
        yield ToolEvent(type="found", message=formatted)
        yield yield_success("SQL formatted successfully.")
    except Exception as e:
        yield yield_error(f"Format error: {str(e)}")
