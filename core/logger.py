import os
import queue
import threading
import time
from datetime import datetime

# A dedicated queue for thread-safe logging across the application
log_queue = queue.Queue()

def log_event(event_type: str, data: any):
    """
    Public API for logging an event.
    Pushes the event to a background queue to ensure the main application 
    logic is never blocked by file I/O.
    """
    log_queue.put((event_type, data))

def _logger_worker():
    """
    Background worker that continuously processes the log queue.
    Implements a robust retry mechanism for Windows file-locking environments.
    """
    log_file = "agent.log"
    
    while True:
        event_type, data = log_queue.get()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{event_type}] {data}\n"
        
        # Retry mechanism for cases where the log file might be temporarily locked
        for attempt in range(5):
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    f.flush()
                break # Success
            except PermissionError:
                # Wait briefly if the file is locked (common on Windows)
                time.sleep(0.1)
            except Exception as e:
                print(f"Logging Failure: {e}")
                break
        
        log_queue.task_done()

# Start the logging thread as a daemon so it exits when the main program stops
threading.Thread(target=_logger_worker, daemon=True).start()
