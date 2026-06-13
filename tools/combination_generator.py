import os
import time
import string
import itertools
import asyncio

def estimate_time(total_combinations):
    # Rough estimate: 5 million combinations per second with buffered writes
    estimated_seconds = total_combinations / 5_000_000
    if estimated_seconds < 1:
        return "Less than 1 second"
    return time.strftime('%H:%M:%S', time.gmtime(estimated_seconds))

async def run(params: dict):
    try:
        length = int(params.get("length", 3))
    except ValueError:
        yield {"type": "error", "message": "Length must be a valid positive integer."}
        return

    output_file = params.get("output_file", "").strip()

    if length <= 0:
        yield {"type": "error", "message": "Length must be greater than 0."}
        return
    if not output_file:
        yield {"type": "error", "message": "Output file path is required."}
        return

    output_file = os.path.expanduser(output_file)
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    chars = string.ascii_letters
    total_combinations = len(chars)**length
    est_time = estimate_time(total_combinations)

    yield {"type": "log", "message": f"Generating {total_combinations:,} combinations..."}
    yield {"type": "log", "message": f"Estimated time: {est_time}"}

    # Open file and write combinations in chunks to maximize I/O speed
    chunk_size = 500000
    generated = 0

    def batched(iterable, n):
        it = iter(iterable)
        while batch := tuple(itertools.islice(it, n)):
            yield batch

    def process_and_write(chunk, file_obj):
        data = "\n".join(map("".join, chunk)) + "\n"
        file_obj.write(data)

    try:
        f = await asyncio.to_thread(open, output_file, 'w', encoding='utf-8')
        try:
            for chunk in batched(itertools.product(chars, repeat=length), chunk_size):
                await asyncio.to_thread(process_and_write, chunk, f)
                generated += len(chunk)
                
                # Yield control to event loop to allow cancellation and update progress
                await asyncio.sleep(0)
                progress_percent = (generated / total_combinations) * 100
                yield {"type": "progress", "percent": progress_percent}

        finally:
            await asyncio.to_thread(f.close)

        yield {"type": "progress", "percent": 100.0}
        yield {"type": "log", "message": f"Combinations successfully saved to: {output_file}"}
        yield {"type": "success", "message": f"Successfully generated {total_combinations:,} combinations."}

    except asyncio.CancelledError:
        yield {"type": "log", "message": "Generation cancelled by user."}
        # Optionally delete incomplete file or keep it
    except Exception as e:
        yield {"type": "error", "message": f"Failed to generate: {str(e)}"}
