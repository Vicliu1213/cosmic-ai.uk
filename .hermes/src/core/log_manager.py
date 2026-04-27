import logging
import queue
import threading
import time

class LogManager:
    def __init__(self, sample_rate=0.1):
        self.sample_rate = sample_rate
        self.log_queue = queue.Queue()
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def _worker(self):
        while True:
            msg = self.log_queue.get()
            if msg:
                logging.info(msg)

    def async_info(self, msg):
        if random.random() < self.sample_rate:
            self.log_queue.put(msg)