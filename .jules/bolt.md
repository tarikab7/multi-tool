## 2023-10-27 - [os.listdir vs os.scandir]
**Learning:** Found a common pattern of using `os.listdir()` followed by `os.path.isdir()` inside a loop. This requires an extra `stat()` system call per file, which is inefficient.
**Action:** Use `os.scandir()` instead, which caches file attributes and significantly improves performance on directories with many files.
