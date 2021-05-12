from numpy import random as nr
from . import exceptions as ex


class Uniform:
    def __init__(self, a, b):
        if not 0 <= a <= b:
            raise ex.ParameterError("Parameters must be 0 <= a <= b")
        self._a = a
        self._b = b

    def generate(self):
        return nr.uniform(self._a, self._b)

class Weibull:
    def __init__(self, a, lamb, mx):
        self._a = a
        self._lamb = lamb
        self.mx = mx

    def generate(self):
        # cur_time = -1 

        cur_time = self._lamb*nr.weibull(self._a)
        while cur_time < 0 or cur_time > 2*self.mx:
            cur_time = self._lamb*nr.weibull(self._a)

        return cur_time
        # return self._lamb*nr.weibull(self._a)

class Normal:
    def __init__(self, mu, sigma):
        self._mu = mu
        self._sigma = sigma

    def generate(self):
        cur_time = nr.normal(self._mu, self._sigma)
        # while cur_time < 0:
        #     cur_time = nr.normal(self._mu, self._sigma)
        while cur_time < 0 or cur_time > 2*self._mu:
            cur_time = nr.normal(self._mu, self._sigma)

        return cur_time
