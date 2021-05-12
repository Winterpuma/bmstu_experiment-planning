from queueing_system.modeller import Modeller
from prettytable import PrettyTable

import matplotlib.pyplot as plt
import numpy as np
import math
import random

FACTORS_NUMBER = 4
MATR_SIZE = 2**FACTORS_NUMBER
MOD_NUMBER = 1 # Лучше бртать 10

class Experiment():
    def __init__(self, gen, pm, time):
        self.min_gen_int = gen[0]
        self.max_gen_int = gen[1]
        self.min_gen_var = gen[2]
        self.max_gen_var = gen[3]

        self.min_pm_int = pm[0]
        self.max_pm_int = pm[1]
        self.min_pm_var = pm[2]
        self.max_pm_var = pm[3]       

        self.time = time
        self.b = []
        self.table = []
    
    def get_matrix(self):
        matrix = [[0 for i in range(MATR_SIZE)] for i in range(MATR_SIZE)]
        
        for i in range(MATR_SIZE):
            for j in range(1, FACTORS_NUMBER + 1):
                if i // (2 ** (FACTORS_NUMBER - j)) % 2 == 1:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = -1

            matrix[i][0] = 1

            # matrix[i][4] = matrix[i][1] * matrix[i][2]
            # matrix[i][5] = matrix[i][1] * matrix[i][3]
            # matrix[i][6] = matrix[i][2] * matrix[i][3]
            # matrix[i][7] = matrix[i][1] * matrix[i][2] * matrix[i][3]

            matrix[i][5] = matrix[i][1] * matrix[i][2]
            matrix[i][6] = matrix[i][1] * matrix[i][3]
            matrix[i][7] = matrix[i][1] * matrix[i][4]
            matrix[i][8] = matrix[i][2] * matrix[i][3]
            matrix[i][9] = matrix[i][2] * matrix[i][4]
            matrix[i][10] = matrix[i][3] * matrix[i][4]

            matrix[i][11] = matrix[i][1] * matrix[i][2] * matrix[i][3]
            matrix[i][12] = matrix[i][1] * matrix[i][2] * matrix[i][4]
            matrix[i][13] = matrix[i][1] * matrix[i][3] * matrix[i][4]
            matrix[i][14] = matrix[i][2] * matrix[i][3] * matrix[i][4]

            matrix[i][15] = matrix[i][1] * matrix[i][2] * matrix[i][3] * matrix[i][4]
            
        return matrix
    
    def calc_xmat(self, plan):
        transposed = np.transpose(plan)
        mat = np.matmul(transposed, np.array(plan))
        mat = np.linalg.inv(mat)
        mat = np.matmul(mat, transposed)
        return mat.tolist()


    def linear(self, b, x):
        res = 0
        linlen = int(np.log2(len(b))) + 1
        for i in range(linlen):
            res += b[i] * x[i]
        return res


    def nonlinear(self, b, x):
        res = 0
        for i in range(len(b)):
            res += b[i] * x[i]
        return res


    def expand_plan(self, plan, y, xmat):
        b = list()
        for i in range(len(xmat)):
            b_cur = 0
            for j in range(len(xmat[i])):
                b_cur += xmat[i][j] * y[j]
            b.append(b_cur)
            # b.append(b_cur/MATR_SIZE)

        ylin = list()
        ynlin = list()
        for i in range(len(plan)):
            ylin.append(self.linear(b, plan[i]))
            ynlin.append(self.nonlinear(b, plan[i]))

        for i in range(len(plan)):
            plan[i].append(y[i])
            plan[i].append(ylin[i])
            plan[i].append(ynlin[i])
            plan[i].append(abs(y[i] - ylin[i]))
            plan[i].append(abs(y[i] - ynlin[i]))

        return plan, b

    def scale_factor(self, x, realmin, realmax, xmin=-1, xmax=1):
        return realmin + (realmax - realmin) * (x - xmin) / (xmax - xmin)

    def param_convert(self, gen_int, gen_var, pm_int, pm_var):
        a = 1/gen_int - math.sqrt(3/gen_var)
        b = 1/gen_int + math.sqrt(3/gen_var)
        if a < 0:
            a = 1e-10
            b = 2/gen_int

        # pm_int = 1/pm_int
        # pm_var = 1/pm_var
        # weib_a = (pm_var/pm_int)**(-1.086)
        # weib_lamb = pm_int/(math.gamma(1 + 1/weib_a))
        # if weib_a < 0:
        #     weib_a = 1e-10
        # if weib_lamb < 0:
        #     weib_lamb = 1e-10

        weib_a = 1/pm_int
        weib_lamb = 1/pm_var
        return a, b, weib_a, weib_lamb


    def calculate(self):
        matrix = self.get_matrix()

        xmat = self.calc_xmat(matrix)

        y = list()
            
        for exp in matrix:
            gen_int = self.scale_factor(exp[1], self.min_gen_int, self.max_gen_int)
            gen_var = self.scale_factor(exp[2], self.min_gen_var, self.max_gen_var)
            pm_int = self.scale_factor(exp[3], self.min_pm_int, self.max_pm_int)
            pm_var = self.scale_factor(exp[4], self.min_pm_var, self.max_pm_var)

            a, b, weib_a, weib_lamb = self.param_convert(gen_int, gen_var, pm_int, pm_var)

            exp_res = 0
            for i in range(MOD_NUMBER):
                model = Modeller(a, b, weib_a, weib_lamb, 1/pm_int) 
                ro, avg_wait_time = model.event_based_modelling(self.time)
                exp_res += avg_wait_time
            exp_res /= MOD_NUMBER
           
            y.append(exp_res)

        plan, self.b = self.expand_plan(matrix, y, xmat)
        return plan, self.b

    def check(self, gen_int, gen_var, pm_int, pm_var):

        exp_res = 0
        for i in range(MOD_NUMBER):
            new_gen_int = self.scale_factor(gen_int, self.min_gen_int, self.max_gen_int)
            new_gen_var = self.scale_factor(gen_var, self.min_gen_var, self.max_gen_var)
            new_pm_int = self.scale_factor(pm_int, self.min_pm_int, self.max_pm_int)
            new_pm_var = self.scale_factor(pm_var, self.min_pm_var, self.max_pm_var)

            a, b, weib_a, weib_lamb = self.param_convert(new_gen_int, new_gen_var, new_pm_int, new_pm_var)
            model = Modeller(a, b, weib_a, weib_lamb, pm_int) 
            ro, avg_wait_time = model.event_based_modelling(self.time)
            exp_res += avg_wait_time
                
        exp_res /= MOD_NUMBER
        # exp_res = avg_ro/((1 - avg_ro)*gen_int)
        # print(exp_res)
        
        lin_res = self.b[0] + self.b[1]*gen_int + self.b[2]*gen_var + self.b[3]*pm_int + self.b[4]*pm_var
        nonlin_res = self.b[0] + self.b[1]*gen_int + self.b[2]*gen_var + self.b[3]*pm_int + self.b[4]*pm_var + \
            self.b[5]*gen_int*gen_var + self.b[6]*gen_int*pm_int + self.b[7]*gen_int*pm_var + \
            self.b[8]*gen_var*pm_int + self.b[9]*gen_var*pm_var + self.b[10]*pm_int*pm_var + \
            self.b[11]*gen_int*gen_var*pm_int + self.b[12]*gen_int*gen_var*pm_var + \
            self.b[13]*gen_int*pm_int*pm_var + self.b[14]*gen_var*gen_var*pm_var + \
            self.b[15]*gen_int*gen_var*pm_int*pm_var
        
        return [gen_int, gen_var, pm_int, pm_var, exp_res, lin_res, nonlin_res]
        

