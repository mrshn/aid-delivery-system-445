import threading
import queue

class MessageQueue():
    active_campaigns = []
    def __init__(self) -> None:
        pass
    def notify(index):
        pass

class MessageQueue:
    def __init__(self):
        self._queue = queue.Queue()
        self._listeners = {}
        self._lock = threading.Lock()

    def emit(self, message, data=None):
        with self._lock:
            self._queue.put((message, data))
            if message in self._listeners:
                for listener in self._listeners[message]:
                    listener.notify()

    def watch(self, callback, campaign_id):
        with self._lock:
            for message in messages:
                if message not in self._listeners:
                    self._listeners[message] = []
                self._listeners[message].append(listener)
        return listener