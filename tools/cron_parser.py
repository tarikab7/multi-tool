import asyncio

async def run(params: dict):
    cron = params.get("cron", "*/5 * * * *").strip()
    
    yield {"type": "log", "message": f"Explaining cron schedule '{cron}'..."}
    await asyncio.sleep(0.5)
    
    parts = cron.split()
    if len(parts) != 5:
        yield {"type": "error", "message": "Cron must have exactly 5 fields (min hour day month weekday)."}
        return
        
    try:
        min_f, hour_f, day_f, month_f, day_w = parts
        
        explanation = []
        
        # Minutes
        if min_f == "*": explanation.append("every minute")
        elif min_f.startswith("*/"): explanation.append(f"every {min_f.split('/')[1]} minutes")
        else: explanation.append(f"at minute {min_f}")
        
        # Hours
        if hour_f == "*": explanation.append("every hour")
        elif hour_f.startswith("*/"): explanation.append(f"every {hour_f.split('/')[1]} hours")
        else: explanation.append(f"at hour {hour_f}")
        
        # Days
        if day_f != "*": explanation.append(f"on day of month {day_f}")
        
        # Months
        if month_f != "*": explanation.append(f"in month {month_f}")
        
        # Weekdays
        if day_w != "*": explanation.append(f"on weekday number {day_w}")
        
        full_text = "Run: " + ", ".join(explanation) + "."
        yield {"type": "found", "message": full_text}
        yield {"type": "success", "message": "Cron translated successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Failed parsing expression: {str(e)}"}
