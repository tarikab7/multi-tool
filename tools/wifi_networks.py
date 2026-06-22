import subprocess
import asyncio
import sys

async def run(params: dict):
    yield {"type": "log", "message": "Scanning network hardware interfaces for nearby Wi-Fi SSIDs..."}
    
    try:
        if sys.platform.startswith("linux"):
            
            cmd = ["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,SECURITY", "device", "wifi", "list"]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                lines = stdout.decode().strip().split("\n")
                found_count = 0
                for line in lines:
                    if line:
                        parts = line.split(":")
                        if len(parts) >= 4:
                            ssid = parts[0] or "<Hidden>"
                            signal = parts[2]
                            sec = parts[3]
                            yield {"type": "found", "message": f"SSID: {ssid} | Signal: {signal}% | Auth: {sec}"}
                            found_count += 1
                yield {"type": "success", "message": f"Scan complete. Discovered {found_count} network(s)."}
            else:
                yield {"type": "error", "message": f"Wlan scan failed: {stderr.decode()}"}
        else:
            yield {"type": "error", "message": "Wi-Fi scan is only supported on Linux platform."}
    except Exception as e:
        yield {"type": "error", "message": f"Interface query failed: {str(e)}"}
