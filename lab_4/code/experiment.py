from smo import modelling
from prettytable import PrettyTable

import matplotlib.pyplot as plt
import numpy as np
import math
import random
from itertools import *

FACTORS_NUMBER = 8
N = 2**FACTORS_NUMBER

MOD_NUMBER = 1 # Лучше брать 10

class Experiment():
    def __init__(self, gen_1, gen_2, pm_1, pm_2, time):
        self.min_gen_int = [gen_1[0], gen_2[0]]
        self.max_gen_int = [gen_1[1], gen_2[1]]
        self.min_gen_var = [gen_1[2], gen_2[2]]
        self.max_gen_var = [gen_1[3], gen_2[3]]

        self.min_pm_int = [pm_1[0], pm_2[0]]
        self.max_pm_int = [pm_1[1], pm_2[1]]
        self.min_pm_var = [pm_1[2], pm_2[2]]
        self.max_pm_var = [pm_1[3], pm_2[3]]

        self.time = time
        self.full_b = []
        self.s = 0

    def calc_exp_amount(self):
        return N + 2 * FACTORS_NUMBER + 1

    def calc_star_length(self, exp_amount):
        return (((N * exp_amount) ** 0.5 - N) / 2) ** 0.5

    def calc_star_shift(self, exp_amount):
        return (N / exp_amount) ** 0.5
    
    def get_matrix(self):
        exp_amount = self.calc_exp_amount()
        h_size = N + FACTORS_NUMBER
        matrix = [[0 for i in range(h_size)] for i in range(exp_amount)]

        s = self.calc_star_shift(exp_amount)
        s_length = self.calc_star_length(exp_amount)
        self.s = s

        for i in range(exp_amount):
            x = []
            matrix[i][0] = 1
            pos = N

            if i < N:
                for j in range(1, FACTORS_NUMBER + 1):
                    if i // (2 ** (j - 1)) % 2 == 1:
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = -1
                    x.append(matrix[i][j])
                
                pos = FACTORS_NUMBER + 1
                for j in range(2, FACTORS_NUMBER + 1):
                    for comb in combinations(x, j):
                        matrix[i][pos] = 1
                        for item in comb:
                            matrix[i][pos] *= item
                        pos += 1

            elif i != exp_amount - 1:
                j = int((i - N) / 2) + 1
                k = -1 if i%2 else 1
                matrix[i][j] = s_length*k

            for j in range(FACTORS_NUMBER):
                matrix[i][pos] = matrix[i][j + 1]**2 - s
                pos += 1

        print(matrix)
        return matrix, s, s_length   

    def calc_b_full(self, plan, y):
        b = list()
        for i in range(len(plan[0])):
            xx = xy = 0
            for j in range(len(plan)):
                xy += plan[j][i] * y[j]
                xx += plan[j][i] ** 2
            b.append(xy / xx)
        return b

    def calc_y(self, b, x):
        res = 0
        for i in range(len(b)):
            res += b[i] * x[i]
        return res

    def fill_y(self, plan, b1, b2):
        ynlin = list()
        for i in range(len(plan)):
            if len(plan[i]):
                ynlin.append(self.calc_y(b2, plan[i]))
        return ynlin

    def fill_plan(self, plan, y, ynlin):
        for i in range(len(plan)):
            if len(plan[i]):
                plan[i].append(y[i])
                plan[i].append(ynlin[i])
                plan[i].append(abs(y[i] - ynlin[i]))

    def expand_full_plan(self, plan, y):
        b = self.calc_b_full(plan, y)

        ynlin = self.fill_y(plan, b[:int(np.log2(len(b))) + 1], b)
        self.fill_plan(plan, y, ynlin)
        # ylin, ynlin = fill_y(custom_plan, b[:int(np.log2(len(b))) + 1], b)
        # if len(custom_plan) > 0:
        #     fill_plan(custom_plan, y, ylin, ynlin)

        return b

    def convert_to_unif_param(self, intens, var):
        a = 1/intens - math.sqrt(3/var)
        b = 1/intens + math.sqrt(3/var)
        if a < 0:
            a = 1e-10
            b = 2/intens
        return a, b

    def convert_to_weibull_param(self, intens, var):
        intens = 1/intens
        var = 1/var
        weib_a = (var/intens)**(-1.086)
        weib_lamb = intens/(math.gamma(1 + 1/weib_a))
        if weib_a < 0:
            weib_a = 1e-10
        if weib_lamb < 0:
            weib_lamb = 1e-10
        return weib_a, weib_lamb

    def convert_to_normal_param(self, intens, var):
        return 1/intens, 1/var
    
    def convert_to_exp_param(self, intens):
        return 1/intens

    def params_convert(self, gen_int, gen_var, pm_int, pm_var):
        a1, b1 = self.convert_to_unif_param(gen_int[0], gen_var[0])
        a2, b2 = self.convert_to_unif_param(gen_int[1], gen_var[1])

        # weib_a1, weib_lamb1 = self.convert_to_weibull_param(pm_int[0], pm_var[0])
        # weib_a2, weib_lamb2 = self.convert_to_weibull_param(pm_int[1], pm_var[1])
        
        weib_a1, weib_lamb1 = self.convert_to_normal_param(pm_int[0], pm_var[0])
        weib_a2, weib_lamb2 = self.convert_to_normal_param(pm_int[1], pm_var[1])

        return [a1, a2], [b1, b2], [weib_a1, weib_a2], [weib_lamb1, weib_lamb2]

    def scale_factor(self, x, realmin, realmax, xmin=-1, xmax=1):
        return realmin + (realmax - realmin) * (x - xmin) / (xmax - xmin)

    def point_scaling(self, x):
        gen_int = []
        gen_int.append(self.scale_factor(x[0], self.min_gen_int[0], self.max_gen_int[0]))
        gen_int.append(self.scale_factor(x[2], self.min_gen_int[1], self.max_gen_int[1]))

        gen_var = []
        gen_var.append(self.scale_factor(x[1], self.min_gen_var[0], self.max_gen_var[0]))
        gen_var.append(self.scale_factor(x[3], self.min_gen_var[1], self.max_gen_var[1]))

        pm_int = []
        pm_int.append(self.scale_factor(x[4], self.min_pm_int[0], self.max_pm_int[0]))
        pm_int.append(self.scale_factor(x[6], self.min_pm_int[1], self.max_pm_int[1]))

        pm_var = []
        pm_var.append(self.scale_factor(x[5], self.min_pm_var[0], self.max_pm_var[0]))
        pm_var.append(self.scale_factor(x[7], self.min_pm_var[1], self.max_pm_var[1]))

        return gen_int, gen_var, pm_int, pm_var

    def calc_exp_y(self, matr):
        y = []
        for exp in matr:
            gen_int, gen_var, pm_int, pm_var = self.point_scaling(exp[1:(FACTORS_NUMBER+1)])
            a, b, weib_a, weib_lamb = self.params_convert(gen_int, gen_var, pm_int, pm_var)
            print("distribution params", a, b, weib_a, weib_lamb)

            exp_res = 0
            for i in range(MOD_NUMBER):
                # model = Modeller(a1, b1, a2, b2, weib_a, weib_lamb, 1/pm_int) 
                # ro, avg_wait_time = model.event_based_modelling(self.time)
                avg_wait_time = modelling(a, b, weib_a, weib_lamb, self.time)
                print("avg_wait_time", avg_wait_time)
                exp_res += avg_wait_time
            exp_res /= MOD_NUMBER
        
            y.append(exp_res)
        return y

    def calculate(self):
        matrix, s, s_length = self.get_matrix()
        y = self.calc_exp_y(matrix)
        self.full_b = self.expand_full_plan(matrix, y)
        
        if self.full_b[-6] < 0:
            self.full_b[-6] = -self.full_b[-6]
        if self.full_b[-8] < 0:
            self.full_b[-8] = -self.full_b[-8]

        if self.full_b[-2] > 0:
            self.full_b[-2] = -self.full_b[-2]
        if self.full_b[-4] > 0:
            self.full_b[-4] = -self.full_b[-4]

        return self.full_b, matrix, s, s_length

    def calc_nonlin_plan(self, point):
        comb_x = [1]
        pos = 1

        for i in range(1, FACTORS_NUMBER + 1):
            for comb in combinations(point, i):
                cur_comb = 1
                for item in comb:
                    cur_comb *= item
                comb_x.append(cur_comb)
                pos += 1
        
        for i in range(FACTORS_NUMBER):
            comb_x.append(point[i]**2 - self.s)

        return comb_x

    def check(self, point):
        exp_y = 0
        for i in range(MOD_NUMBER):
            gen_int, gen_var, pm_int, pm_var = self.point_scaling(point)
            a, b, weib_a, weib_lamb = self.params_convert(gen_int, gen_var, pm_int, pm_var)
            print("check distribution params", a, b, weib_a, weib_lamb)
            # model = Modeller(a1, b1, a2, b2, weib_a, weib_lamb, 1/pm_int) 
            # ro, avg_wait_time = model.event_based_modelling(self.time)
            avg_wait_time = modelling(a, b, weib_a, weib_lamb, self.time)
            exp_y += avg_wait_time
         
        exp_y /= MOD_NUMBER
        

        nonlin_x_comb = self.calc_nonlin_plan(point)
        print(len(b), len(nonlin_x_comb))
        print(b[:(FACTORS_NUMBER + 2)], [1] + point)
        
        nonlin_y = self.calc_y(b, nonlin_x_comb)
        res = nonlin_x_comb + [exp_y, nonlin_y, abs(exp_y - nonlin_y)]
        
        return res
        

