## 2024-05-30 - Faster Directory Browsing
**Learning:** `os.scandir` is significantly faster than `os.listdir` followed by `os.path.isdir` because it caches the `stat()` syscalls. On large directories, it can improve iteration speed by over 70%.
**Action:** Always prefer `os.scandir` when traversing directories, especially if file attributes (like whether it is a directory) are needed. Keep in mind it returns `DirEntry` objects rather than strings.
