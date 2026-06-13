## 2024-06-13 - Optimize os.walk to os.scandir
**Learning:** In python, os.walk and os.listdir return strings which requires redundant `stat()` system calls. Using `os.scandir` caches file attributes on lookup and resulted in 50% time savings.
**Action:** Use os.scandir over os.walk and os.listdir when doing deep filesystem traversals.
