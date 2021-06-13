import sys
from os import environ
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from experiment import Experiment
from plan_table_controller import PlanTableController
from numpy import random as nr
from itertools import *
from table import ExcelTable

from experiment import FACTORS_NUMBER, CHECK_FULL, CHECK_PARTIAL 

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi("window.ui", self)
        self.table_full_widget = PlanTableController('ПФЭ.xlsx')
        self.table_partial_widget = PlanTableController('ДФЭ.xlsx')
        self.experiment = None
        self.plan_table_full = None
        self.plan_table_partial = None
        self.b_full = None
        self.b_partial = None
        self.full_table_position = 1
        self.partial_table_position = 1


    @pyqtSlot(name='on_calc_button_clicked')
    def parse_parameters(self):
        try:
            ui = self.ui
            
            min_gen_int_1 = float(ui.line_edit_min_gen_int.text())
            max_gen_int_1 = float(ui.line_edit_max_gen_int.text())
            min_gen_var_1 = float(ui.line_edit_min_gen_var.text())
            max_gen_var_1 = float(ui.line_edit_max_gen_var.text())
            gen_1 = [min_gen_int_1, max_gen_int_1, min_gen_var_1, max_gen_var_1]

            min_gen_int_2 = float(ui.line_edit_min_gen_int_2.text())
            max_gen_int_2 = float(ui.line_edit_max_gen_int_2.text())
            min_gen_var_2 = float(ui.line_edit_min_gen_var_2.text())
            max_gen_var_2 = float(ui.line_edit_max_gen_var_2.text())
            gen_2 = [min_gen_int_2, max_gen_int_2, min_gen_var_2, max_gen_var_2]

            min_pm_int_1 = float(ui.line_edit_min_pm_int_1.text())
            max_pm_int_1 = float(ui.line_edit_max_pm_int_1.text())
            min_pm_var_1 = float(ui.line_edit_min_pm_var_1.text())
            max_pm_var_1 = float(ui.line_edit_max_pm_var_1.text())
            pm_1 = [min_pm_int_1, max_pm_int_1, min_pm_var_1, max_pm_var_1]

            min_pm_int_2 = float(ui.line_edit_min_pm_int_2.text())
            max_pm_int_2 = float(ui.line_edit_max_pm_int_2.text())
            min_pm_var_2 = float(ui.line_edit_min_pm_var_2.text())
            max_pm_var_2 = float(ui.line_edit_max_pm_var_2.text())
            pm_2 = [min_pm_int_2, max_pm_int_2, min_pm_var_2, max_pm_var_2]

            if gen_1[0] < 0 or gen_1[1] < 0 or gen_1[2] < 0 or gen_1[3] < 0 or \
                gen_2[0] < 0 or gen_2[1] < 0 or gen_2[2] < 0 or gen_2[3] < 0 or \
                pm_1[0] < 0 or pm_1[1] < 0 or pm_1[2] < 0 or pm_1[3] < 0 or \
                pm_2[0] < 0 or pm_2[1] < 0 or pm_2[2] < 0 or pm_2[3] < 0:
                raise ValueError('Интенсивности и дисперсии интенсивностей должны быть > 0')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            self.experiment = Experiment(gen_1, gen_2, pm_1, pm_2, time)
            self.b_full, self.b_partial, self.plan_table_full, self.plan_table_partial = self.experiment.calculate()

            '''
            print('\n\n\n')
            print('b_full\n', len(self.b_full), self.b_full)
            print('b_partial\n', len(self.b_partial), self.b_partial)
            print('plan_table_full\n', len(self.plan_table_full), self.plan_table_full)
            print('plan_table_partial\n', len(self.plan_table_partial), self.plan_table_partial)
            print('\n\n\n')
            '''
            self.show_results()  

        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', e)

    def set_value(self, table, line, column, format, value):
        item = QTableWidgetItem(format % value)
        item.setTextAlignment(Qt.AlignRight)
        table.setItem(line, column, item)

    def get_nonlin_regr_format_string(self, regr, factors_number):
        x = []
        for i in range(FACTORS_NUMBER):
            x.append("x%d" % (i + 1))

        res_str = "y = %.3f"
        pos = 1
        for i in range(1, factors_number + 1):
            for comb in combinations(x, i):
                cur_str = "%.3f"
                if regr[pos] < 0:
                    cur_str = " - " + cur_str
                    regr[pos] = abs(regr[pos])
                else:
                    cur_str = " + " + cur_str

                for item in comb:
                    cur_str += item
                res_str += cur_str
                pos += 1

        return res_str

    def get_regr_string(self, b, factors_number):
        nonlin_regr_format_str = self.get_nonlin_regr_format_string(b, factors_number)
        nonlin_regr_str = (nonlin_regr_format_str % tuple(b))

        lin_regr_list = b[:(FACTORS_NUMBER + 1)]
        pos = nonlin_regr_format_str.find("x%d" % FACTORS_NUMBER) + 2
        lin_regr_format_str = nonlin_regr_format_str[:pos]
        lin_regr_str = (lin_regr_format_str % tuple(lin_regr_list))

        return lin_regr_str, nonlin_regr_str


    def show_results(self):
        ui = self.ui

        lin_regr_str_full, nonlin_regr_str_full = self.get_regr_string(self.b_full, 2)
        lin_regr_str_partial, nonlin_regr_str_partial = self.get_regr_string(self.b_partial, 2)

        ui.line_edit_lin_regr_full.setText(str(lin_regr_str_full))
        ui.line_edit_nonlin_regr_full.setText(str(nonlin_regr_str_full))
        ui.line_edit_lin_regr_partial.setText(str(lin_regr_str_partial))
        ui.line_edit_nonlin_regr_partial.setText(str(nonlin_regr_str_partial))

    @pyqtSlot(name='on_check_full_button_clicked')
    def parse_check_full_parameters(self):
        try:
            ui = self.ui

            if self.experiment == None:
                raise ValueError('Сначала необходимо рассчитать коэффициенты регрессии')
            
            gen_int_1 = float(ui.line_edit_x1_full.text())
            gen_var_1 = float(ui.line_edit_x2_full.text())
            gen_int_2 = float(ui.line_edit_x3_full.text())
            gen_var_2 = float(ui.line_edit_x4_full.text())
            pm_int_1 = float(ui.line_edit_x5_full.text())
            pm_var_1 = float(ui.line_edit_x6_full.text())
            pm_int_2 = float(ui.line_edit_x7_full.text())
            pm_var_2 = float(ui.line_edit_x8_full.text())

            if abs(gen_int_1) > 1 or abs(gen_var_1) > 1 or abs(gen_int_2) > 1 or abs(gen_var_2) > 1 or \
                abs(pm_int_1) > 1 or abs(pm_var_1) > 1 or abs(pm_int_2) > 1 or abs(pm_var_2) > 1:
                raise ValueError('Координаты точки должны находится в диапазоне [-1; 1]')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            point = [gen_int_1, gen_var_1, gen_int_2, gen_var_2, pm_int_1, pm_var_1, pm_int_2, pm_var_2]
            res = self.experiment.check(point, CHECK_FULL)

            self.show_check_result(res, self.table_full_widget)        

        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', e)


    @pyqtSlot(name='on_check_partial_button_clicked')
    def parse_check_partial_parameters(self):
        try:
            ui = self.ui

            if self.experiment == None:
                raise ValueError('Сначала необходимо рассчитать коэффициенты регрессии')
            
            gen_int_1 = float(ui.line_edit_x1_partial.text())
            gen_var_1 = float(ui.line_edit_x2_partial.text())
            gen_int_2 = float(ui.line_edit_x3_partial.text())
            gen_var_2 = float(ui.line_edit_x4_partial.text())
            pm_int_1 = float(ui.line_edit_x5_partial.text())
            pm_var_1 = float(ui.line_edit_x6_partial.text())
            pm_int_2 = float(ui.line_edit_x7_partial.text())
            pm_var_2 = float(ui.line_edit_x8_partial.text())

            if abs(gen_int_1) > 1 or abs(gen_var_1) > 1 or abs(gen_int_2) > 1 or abs(gen_var_2) > 1 or \
                abs(pm_int_1) > 1 or abs(pm_var_1) > 1 or abs(pm_int_2) > 1 or abs(pm_var_2) > 1:
                raise ValueError('Координаты точки должны находится в диапазоне [-1; 1]')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            point = [gen_int_1, gen_var_1, gen_int_2, gen_var_2, pm_int_1, pm_var_1, pm_int_2, pm_var_2]
            res = self.experiment.check(point, CHECK_PARTIAL)

            self.show_check_result(res, self.table_partial_widget)

        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', e)


    def show_check_result(self, res, table_widget):
        table_widget.addRow(res)

    
    @pyqtSlot(name='on_show_full_table_button_clicked')
    def show_table_full(self):
        self.table_full_widget.show(self.plan_table_full)


    @pyqtSlot(name='on_show_partial_table_button_clicked')
    def show_table_partial(self):
        self.table_partial_widget.show(self.plan_table_partial)
        

def qt_app():
    suppress_qt_warnings()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
    