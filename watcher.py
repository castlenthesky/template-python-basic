import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Define the directory to watch and the command to rerun your program
directory_to_watch = "./src/"
command_to_run = "python -B ./src/main.py"
cooldown_period = 2  # Set the cooldown period in seconds

class MyHandler(FileSystemEventHandler):
    ignore_patterns = ["*/__pycache__/*"]

    def on_modified(self, event):
        # When a file is modified, execute the specified command
        print(f"Received event: {event}")
        # print(f"File {event.src_path} was modified. Re-running the program...")
        time.sleep(cooldown_period)  # Add a cooldown period
        subprocess.call(command_to_run, shell=True)

if __name__ == "__main__":
    time.sleep(2)
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
