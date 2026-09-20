import os

BASE_DIR = r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map"

def print_tree(directory, prefix=""):
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return
        
    entries = [e for e in entries if e not in ("__pycache__", ".git", "node_modules", ".pytest_cache")]
    
    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = (i == len(entries) - 1)
        
        connector = "\\-- " if is_last else "|-- "
        print(f"{prefix}{connector}{entry}")
        
        if os.path.isdir(path):
            extension = "    " if is_last else "|   "
            print_tree(path, prefix + extension)

print("TwinQ-Map/")
print_tree(BASE_DIR)
