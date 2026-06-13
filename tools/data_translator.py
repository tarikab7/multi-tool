import os
import csv
import json
import asyncio

def convert_csv_to_json(csv_path, json_path, delimiter):
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=4)
    return len(rows)

def convert_json_to_csv(json_path, csv_path, delimiter):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of objects.")

    if not data:
        raise ValueError("JSON list is empty.")

    # Extract headers
    headers = list(data[0].keys())

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    return len(data)

async def run(params: dict):
    direction = params.get("direction", "csv_to_json") # "csv_to_json" or "json_to_csv"
    delimiter = params.get("delimiter", ",").strip() or ","
    input_path = params.get("input_path", "").strip()
    output_path = params.get("output_path", "").strip()

    if not input_path or not output_path:
        yield {"type": "error", "message": "Both input and output file paths are required."}
        return

    input_path = os.path.expanduser(input_path)
    output_path = os.path.expanduser(output_path)

    if not os.path.isfile(input_path):
        yield {"type": "error", "message": f"Input file '{input_path}' not found."}
        return

    # Create parent folder for output if needed
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    try:
        if direction == "csv_to_json":
            yield {"type": "log", "message": f"Converting CSV file to JSON..."}
            count = await asyncio.to_thread(convert_csv_to_json, input_path, output_path, delimiter)
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Successfully translated {count} rows. Saved to: {output_path}"}
            yield {"type": "success", "message": "CSV to JSON translation completed."}
        else:
            yield {"type": "log", "message": f"Converting JSON file to CSV..."}
            count = await asyncio.to_thread(convert_json_to_csv, input_path, output_path, delimiter)
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Successfully translated {count} rows. Saved to: {output_path}"}
            yield {"type": "success", "message": "JSON to CSV translation completed."}

    except Exception as e:
        yield {"type": "error", "message": f"Translation failed: {str(e)}"}
