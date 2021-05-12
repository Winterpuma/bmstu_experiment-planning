class Generator:
    def __init__(self, generator):
        self._generator = generator
        self._receivers = set()
        self.intensity = 0
        self.request_count = 0

    def add_receiver(self, receiver):
        self._receivers.add(receiver)

    def remove_receiver(self, receiver):
        try:
            self._receivers.remove(receiver)
        except KeyError:
            pass

    def next_time(self):
        new_time = self._generator.generate()
        self.intensity += new_time
        self.request_count += 1
        return new_time

    def emit_request(self):
        for receiver in self._receivers:
            receiver.receive_request()
    
    def get_avg_intensity(self):
        return 1/(self.intensity/self.request_count)
