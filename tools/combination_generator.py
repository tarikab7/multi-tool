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
    chunk_size = 50000
    buffer = []
    generated = 0

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for combo in itertools.product(chars, repeat=length):
                buffer.append(''.join(combo) + '\n')
                generated += 1

                # Write chunk
                if len(buffer) >= chunk_size:
                    f.writelines(buffer)
                    buffer = []
                    # Yield control to event loop to allow cancellation
                    await asyncio.sleep(0.001)
                    progress_percent = (generated / total_combinations) * 100
                    yield {"type": "progress", "percent": progress_percent}

            # Write remaining
            if buffer:
                f.writelines(buffer)
                
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Combinations successfully saved to: {output_file}"}
            yield {"type": "success", "message": f"Successfully generated {total_combinations:,} combinations."}

    except asyncio.CancelledError:
        yield {"type": "log", "message": "Generation cancelled by user."}
        # Optionally delete incomplete file or keep it
    except Exception as e:
        yield {"type": "error", "message": f"Failed to generate: {str(e)}"}
