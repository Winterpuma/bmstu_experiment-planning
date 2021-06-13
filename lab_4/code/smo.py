import math

import numpy.random as nr

STEP = 0.1

class UniformGenerator:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def generation_time(self):
        return nr.uniform(self.a, self.b)

class ExponentGenerator:
    def __init__(self, lambda_param):
        self.lambda_param = lambda_param

    def generation_time(self):
        return nr.exponential(self.lambda_param)

class NormalGenerator:
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

    def generation_time(self):
        cur_time = nr.normal(self.mu, self.sigma)
        while cur_time < 0 or cur_time > 2*self.mu:
            cur_time = nr.normal(self.mu, self.sigma)

        return cur_time


class RequestGenerator:
    def __init__(self, generator, numGen: str):
        self._generator = generator
        self._receivers = set()
        self.time_periods = []
        self.numGen = numGen

    def add_receiver(self, receiver):
        self._receivers.add(receiver)

    def remove_receiver(self, receiver):
        try:
            self._receivers.remove(receiver)
        except KeyError:
            pass

    def next_time_period(self):
        time = self._generator.generation_time()
        self.time_periods.append(time)
        return time

    def emit_request(self):
        for receiver in self._receivers:
            receiver.receive_request(self.numGen)


class RequestProcessor:
    def __init__(self, generator1, generator2, len_queue=0, reenter_probability=0):
        self._generator1 = generator1
        self._generator2 = generator2
        self._current_queue = []
        self._max_queue_size = 0
        self._processed_requests = 0
        self._reenter_probability = reenter_probability
        self._reentered_requests = 0
        self._len_queue = len_queue
        self.time_periods = []
        self.last_type_request = '1'

    @property
    def processed_requests(self):
        return self._processed_requests

    @property
    def current_queue_size(self):
        return len(self._current_queue)

    def process(self):
        global current_time
        global time_processed_request
        if len(self._current_queue) > 0:
            time_processed_request.append(current_time)
            self._processed_requests += 1
            self.last_type_request = self._current_queue.pop()

    def receive_request(self, type_request: str):
        self._current_queue.insert(0, type_request)

    def next_time_period(self):
        if self.last_type_request == '1':
            time = self._generator1.generation_time()
        else:
            time = self._generator2.generation_time()

        self.time_periods.append(time)
        return time

current_time = 0
time_processed_request = []
class Modeller:
    def __init__(self, generator1, generator2, processor):
        self._generator1 = generator1
        self._generator2 = generator2
        self._processor = processor
        self._generator1.add_receiver(self._processor)
        self._generator2.add_receiver(self._processor)

    def time_based_modelling(self, dt, time_modelling):
        global current_time
        global time_processed_request
        global p_teor
        time_processed_request.clear()
        current_time = 0
        generator1 = self._generator1
        generator2 = self._generator2
        processor = self._processor
        queue_size = [0]
        time_generated_request = []
        num_requests = [0]

        gen_period1 = generator1.next_time_period()
        gen_period2 = generator2.next_time_period()
        proc_period = min(gen_period1, gen_period2) + processor.next_time_period()

        while current_time < time_modelling:
            if gen_period1 <= current_time:
                time_generated_request.append(current_time)
                generator1.emit_request()
                gen_period1 += generator1.next_time_period()
            if gen_period2 <= current_time:
                time_generated_request.append(current_time)
                generator2.emit_request()
                gen_period2 += generator2.next_time_period()
            if proc_period <= current_time:
                processor.process()

                if processor.current_queue_size > 0:
                    proc_period += processor.next_time_period()
                else:
                    proc_period = min(gen_period1, gen_period2) + processor.next_time_period()
            queue_size.append(processor.current_queue_size)


            current_time += dt

        lambda_fact = 1 / (sum(generator1.time_periods) / len(generator1.time_periods))
        mu_fact = 1 / (sum(processor.time_periods) / len(processor.time_periods))
        p = lambda_fact / mu_fact
        num_reports_teor = p / (1 - p)
        num_reports_fact = sum(queue_size) / len(queue_size)
        k = num_reports_fact / num_reports_teor

        # if p_teor >= 1 or p_teor <= 0 or k == 0:
        #     k = 1

        if len(time_processed_request):
            mas_time_request_in_smo = []
            for i in range(len(time_processed_request)):
                # print(time_processed_request[i] - time_generated_request[i])
                mas_time_request_in_smo.append(time_processed_request[i] - time_generated_request[i])
            # print(mas_time_request_in_smo)
            # print(mas_time_request_in_smo)
            avg_time_in_smo = sum(mas_time_request_in_smo) / len(mas_time_request_in_smo)
        else:
            avg_time_in_smo = 0

        result = avg_time_in_smo
        return result

def modelling(gen_int, gen_var, pm_int, pm_var, time_modelling):
    generator1 = RequestGenerator(UniformGenerator(gen_int[0], gen_var[0]), '1')
    generator2 = RequestGenerator(UniformGenerator(gen_int[1], gen_var[1]), '2')
    OA_type1 = NormalGenerator(pm_int[0], pm_var[0])
    OA_type2 = NormalGenerator(pm_int[1], pm_var[1])
    processor = RequestProcessor(OA_type1, OA_type2)
    model = Modeller(generator1, generator2, processor)
    result_tb = model.time_based_modelling(STEP, time_modelling)
    return result_tb