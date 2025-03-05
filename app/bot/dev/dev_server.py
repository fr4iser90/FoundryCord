# dev_server.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import sys

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()
    
    def start_bot(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("Starting bot...")
        self.process = subprocess.Popen([sys.executable, "-m", "core.main"])
    
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}")
            self.start_bot()

if __name__ == "__main__":
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='app/bot', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()