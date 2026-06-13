import os
import re
import asyncio

def perform_rename_sync(directory, search_pattern, replace_pattern, use_regex, casing):
    renamed = []
    
    # List top level files only to keep safety
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            continue

        base, ext = os.path.splitext(filename)
        new_base = base

        # Search and replace
        if use_regex:
            try:
                new_base = re.sub(search_pattern, replace_pattern, base)
            except Exception:
                # Invalid regex, ignore substitution
                pass
        else:
            new_base = base.replace(search_pattern, replace_pattern)

        # Casing adjustment
        if casing == "lower":
            new_base = new_base.lower()
        elif casing == "upper":
            new_base = new_base.upper()
        elif casing == "title":
            new_base = new_base.title()

        new_filename = f"{new_base}{ext}"
        
        # Perform rename if filename changed
        if new_filename != filename:
            new_filepath = os.path.join(directory, new_filename)
            
            # Avoid overwriting
            counter = 1
            while os.path.exists(new_filepath):
                new_filename = f"{new_base}_{counter}{ext}"
                new_filepath = os.path.join(directory, new_filename)
                counter += 1
                
            try:
                os.rename(filepath, new_filepath)
                renamed.append((filename, new_filename))
            except Exception:
                pass

    return renamed

async def run(params: dict):
    directory = params.get("directory", "").strip()
    search_pattern = params.get("search_pattern", "")
    replace_pattern = params.get("replace_pattern", "")
    use_regex = params.get("use_regex", "false") == "true"
    casing = params.get("casing", "none") # "none", "lower", "upper", "title"

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    yield {"type": "log", "message": f"Scanning files in '{directory}' for renaming..."}
    
    renamed = await asyncio.to_thread(
        perform_rename_sync, directory, search_pattern, replace_pattern, use_regex, casing
    )

    total_renamed = len(renamed)
    if total_renamed == 0:
        yield {"type": "log", "message": "No files matched the search criteria. 0 files renamed."}
        yield {"type": "success", "message": "Completed. 0 files renamed."}
        return

    yield {"type": "log", "message": f"Successfully renamed {total_renamed} file(s):"}
    for idx, (old, new) in enumerate(renamed, 1):
        yield {"type": "log", "message": f"  [{idx}/{total_renamed}] {old} ➔ {new}"}

    yield {"type": "progress", "percent": 100.0}
    yield {"type": "success", "message": f"Successfully renamed {total_renamed} files."}
