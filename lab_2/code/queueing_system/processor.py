from numpy import random as nr
from .generator import Generator


class Processor(Generator):
    def __init__(self, generator, reenter_probability=0):
        super().__init__(generator)
        self._current_queue_size = 0
        self._max_queue_size = 0
        self._processed_requests = 0
        self._reenter_probability = reenter_probability
        self._reentered_requests = 0

    def process(self):
        if self._current_queue_size > 0:
            self._processed_requests += 1
            self._current_queue_size -= 1
            self.emit_request()
            if nr.random_sample() <= self._reenter_probability:
                self._reentered_requests += 1
                self._processed_requests -= 1
                self.receive_request()

    def receive_request(self):
        self._current_queue_size += 1
        if self._current_queue_size > self._max_queue_size:
            self._max_queue_size = self._current_queue_size

    @property
    def processed_requests(self):
        return self._processed_requests

    @property
    def max_queue_size(self):
        return self._max_queue_size

    @property
    def current_queue_size(self):
        return self._current_queue_size

    @property
    def reentered_requests(self):
        return self._reentered_requests
