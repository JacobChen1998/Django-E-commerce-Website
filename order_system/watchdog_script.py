import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .views import update_products

class ProductFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("products.txt"):
            update_products()

if __name__ == "__main__":
    event_handler = ProductFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
