import os
import re
import asyncio

def match_file_lines_sync(file_path, pattern):
    matches = []
    regex = re.compile(pattern)
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            match_objects = list(regex.finditer(line))
            if match_objects:
                # Store line number, matching content, and matching groups
                for m in match_objects:
                    matches.append((line_num, line, m.group(0), m.groups()))
                    # Cap matches at 500 to prevent web crashes
                    if len(matches) >= 500:
                        return matches, True
    return matches, False

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    pattern = params.get("pattern", "").strip()

    if not file_path or not pattern:
        yield {"type": "error", "message": "Both file path and regex pattern are required."}
        return

    file_path = os.path.expanduser(file_path)
    if not os.path.isfile(file_path):
        yield {"type": "error", "message": f"File '{file_path}' not found."}
        return

    yield {"type": "log", "message": f"Searching matching lines in: {os.path.basename(file_path)}..."}

    try:
        matches, capped = await asyncio.to_thread(match_file_lines_sync, file_path, pattern)
        total_matches = len(matches)

        if total_matches == 0:
            yield {"type": "log", "message": "No matching lines found."}
            yield {"type": "success", "message": "Search completed. 0 matches found."}
            return

        yield {"type": "log", "message": f"Found {total_matches} match(es):"}
        for line_num, line, matched_text, groups in matches[:100]: # log first 100 in console to keep clean
            grp_str = f" Groups: {groups}" if groups else ""
            yield {"type": "log", "message": f"  Line {line_num}: '{matched_text}'{grp_str} ➔ {line[:120]}..."}

        if capped:
            yield {"type": "log", "message": "Warning: Matches output capped at 500 entries to prevent memory overflow."}

        yield {"type": "progress", "percent": 100.0}
        yield {"type": "success", "message": f"Completed. Found {total_matches} matches."}

    except Exception as e:
        yield {"type": "error", "message": f"Regex matching failed: {str(e)}"}
