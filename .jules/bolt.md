## 2026-06-16 - Use os.scandir over os.listdir for faster file traversal
**Learning:** Using `os.listdir()` combined with `os.path.isdir()` causes redundant stat() system calls for each file. Using `os.scandir()` caches the file type and avoids these calls, leading to measurable performance improvements, especially in directories with many files.
**Action:** Replace `os.listdir` with `os.scandir` in file traversal endpoints (like `/api/browse`) to reduce I/O overhead.
