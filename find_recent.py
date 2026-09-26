import os
import time

def find_recent_files(directory, hours=2):
    now = time.time()
    for root, _, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(path)
                if now - mtime < hours * 3600:
                    print(f"{time.ctime(mtime)}: {path}")
            except Exception:
                pass

if __name__ == "__main__":
    find_recent_files(".")
