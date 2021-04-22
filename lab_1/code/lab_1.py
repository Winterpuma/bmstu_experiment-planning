import numpy.random as nr
import sys

from prettytable import PrettyTable
import matplotlib.pyplot as plt
import matplotlib as mpl

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

from mainwindow import Ui_MainWindow

# Равномерное
class UniformGenerator:
    def __init__(self, intensivity, range):
        self._a = intensivity - range
        self._b = intensivity + range

    def generation_time(self):
        return nr.uniform(self._a, self._b)

# Нормальное
class GaussGenerator:
    def __init__(self, m, sigma):
        self.m = m
        self.sigma = sigma

    def generation_time(self):
        return nr.normal(self.m, self.sigma)

# Экспотенциальное
class ExponentGenerator:
    def __init__(self, lambda_param):
        self.lambda_param = lambda_param

    def generation_time(self):
        return nr.exponential(1/self.lambda_param)


class RequestGenerator:
    def __init__(self, generator):
        self._generator = generator
        self._receivers = set()
        self.time_periods = []

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
            receiver.receive_request()


class RequestProcessor:
    def __init__(self, generator, len_queue=0, reenter_probability=0):
        self._generator = generator
        self._current_queue_size = 0
        self._max_queue_size = 0
        self._processed_requests = 0
        self._reenter_probability = reenter_probability
        self._reentered_requests = 0
        self._len_queue = len_queue
        self._num_lost_requests = 0
        self.time_periods = []

    @property
    def processed_requests(self):
        return self._processed_requests

    @property
    def lost_requests(self):
        return self._num_lost_requests

    @property
    def max_queue_size(self):
        return self._max_queue_size

    @property
    def current_queue_size(self):
        return self._current_queue_size

    @property
    def reentered_requests(self):
        return self._reentered_requests

    def process(self):
        if self._current_queue_size > 0:
            time_processed_request.append(current_time)
            self._processed_requests += 1
            self._current_queue_size -= 1

    def receive_request(self):
        self._current_queue_size += 1
        if self._current_queue_size > self._max_queue_size:
            self._max_queue_size += 1

    def next_time_period(self):
        time = self._generator.generation_time()
        self.time_periods.append(time)
        return time

current_time = 0
time_processed_request = []
class Modeller:
    def __init__(self, generator, processor):
        self._generator = generator
        self._processor = processor
        self._generator.add_receiver(self._processor)

    def time_based_modelling(self, dt, time_modelling):
        global current_time
        global time_processed_request
        global p_teor
        time_processed_request.clear()
        current_time = 0
        generator = self._generator
        processor = self._processor
        queue_size = [0]
        time_generated_request = []
        num_requests = [0]


        gen_period = generator.next_time_period()
        proc_period = gen_period + processor.next_time_period()

        while current_time < time_modelling :
            num = num_requests[-1]
            if gen_period <= current_time:
                time_generated_request.append(current_time)
                generator.emit_request()
                num += 1
                gen_period += generator.next_time_period()
            if proc_period <= current_time:
                if processor.current_queue_size > 0:
                    num -= 1
                processor.process()

                if processor.current_queue_size > 0:
                    proc_period += processor.next_time_period()
                else:
                    proc_period = gen_period + processor.next_time_period()
            queue_size.append(processor.current_queue_size)


            current_time += dt
            num_requests.append(num)

        lambda_fact = 1 / (sum(generator.time_periods) / len(generator.time_periods))
        mu_fact = 1 / (sum(processor.time_periods) / len(processor.time_periods))
        p = lambda_fact / mu_fact
        num_reports_teor = p / (1 - p)
        num_reports_fact = sum(queue_size) / len(queue_size)
        k = num_reports_fact / num_reports_teor

        if p_teor >= 1 or p_teor <= 0 or k == 0:
            k = 1

        if (len(time_processed_request)):
            mas_time_request_in_smo = []
            for i in range(len(time_processed_request)):
                mas_time_request_in_smo.append(time_processed_request[i] - time_generated_request[i])
            avg_time_in_smo = sum(mas_time_request_in_smo) / len(mas_time_request_in_smo) / k
        else:
            avg_time_in_smo = 0

        result = [
            processor.processed_requests,
            processor.reentered_requests,
            processor.max_queue_size,
            current_time,
            sum(queue_size) / len(queue_size),
            lambda_fact,
            mu_fact,
            avg_time_in_smo
        ]
        return result

def create_graph():
    i = 0.001
    mas = []
    res = []
    while i < 1.01:
        print(i)
        mas_i = []
        for j in range(100):
            step = 0.1
            time_modelling = 10000
            intensivity_gen = i
            intensivity_proc = 1
            range_proc = 1
            generator = RequestGenerator(GaussGenerator(1 / intensivity_gen, 1 / 0.1))
            OA = UniformGenerator(1 / intensivity_proc, 1 / range_proc)
            processor = RequestProcessor(OA)
            model = Modeller(generator, processor)
            result = model.time_based_modelling(step, time_modelling)[7]
            mas_i.append(result)
        mas.append(i)
        res.append(sum(mas_i)/(len(mas_i)+1))
        mas_i.clear()

        if i < 0.1:
            i += 0.01
        else:
            i += 0.1

    mpl.style.use('seaborn')
    plt.plot(mas, res, '#d3b3ff')
    plt.grid(True)
    plt.title("Генератор: нормальный; ОА: равномерный")
    plt.ylabel('Время пребывания заявки в СМО')
    plt.xlabel('Загрузка системы')
    plt.show()

def main():
    intensivity_gen = 3
    intensivity_proc = 4
    range_proc = 1

    step = 0.1
    time_modelling = 10000

    generator = RequestGenerator(GaussGenerator(intensivity_gen))
    OA = UniformGenerator(1 / intensivity_proc, range_proc)
    processor = RequestProcessor(OA)
    model = Modeller(generator, processor)
    result_tb = model.time_based_modelling(step, time_modelling)

    p = intensivity_gen / intensivity_proc
    table = PrettyTable()
    column1 = ''
    names = [column1, 'Теоретич.', 'Фактич.']
    table.field_names = names
    row = ['Загруженность системы', round(p, 2), round(result_tb[5] / result_tb[6], 3)]
    table.add_row(row)
    # row = ['Средняя длина очереди', round(p ** 2 / (1 - p), 2)]
    # table.add_row(row)
    # row = ['Среднее время ожидания заявки в очереди', round((p ** 2) / ((1 - p) * intensivity_gen), 2)]
    # table.add_row(row)
    # row = ['Среднее число заявок в СМО', round(p / (1 - p), 2)]
    # table.add_row(row)
    row = ['Среднее время пребывания заявки в СМО', round(p / (1 - p) / intensivity_gen, 2), round(result_tb[7], 2)]
    table.add_row(row)
    # row = ['----------------', '--------']
    # table.add_row(row)
    row = ['Обработанные заявки', '********', result_tb[0]]
    table.add_row(row)
    # row = ['Максимальная длина очереди', result_tb[2]]
    # table.add_row(row)
    row = ['Общее время моделирования', '********', round(result_tb[3], 3)]
    table.add_row(row)
    # row = ['Загруженность системы', round(result_tb[5] / result_tb[6], 3)]
    # table.add_row(row)
    # row = ['Средняя длина очереди', round(result_tb[4], 3)]
    # table.add_row(row)

    # num_reports_teor = p / (1 - p)
    # num_reports_fact = result_tb[4]
    # k = num_reports_fact / num_reports_teor
    # row = ['Среднее время пребывания заявки в СМО', round(result_tb[7], 2)]
    # table.add_row(row)

    table.align = 'r'
    table.align[column1] = "l"
    print(table)
    print(str(table))
    # create_graph()


p_teor = 0
class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_model.clicked.connect(self.onModelBtnClick)
        self.ui.pushButton_graph.clicked.connect(self.onGraphBtnClick)

    def addItemTableWidget(self, row, column, value):
        item = QTableWidgetItem()
        item.setText(str(value))
        self.ui.tableWidget.setItem(row, column, item)

    def onModelBtnClick(self):
        try:
            global p_teor
            intensivity_gen = self.ui.spinbox_intensivity_gen.value()
            range_gen = self.ui.spinbox_intensivity_gen_range.value()
            intensivity_proc = self.ui.spinbox_intensivity_oa.value()
            range_proc = self.ui.spinbox_intensivity_oa_range.value()
            time_modelling = self.ui.spinbox_time_model.value()

            step = 0.1

            generator = RequestGenerator(GaussGenerator(intensivity_gen, range_gen))
            if range_proc == 0:
                OA = UniformGenerator(1 / intensivity_proc, 0)
            else:
                OA = UniformGenerator(1 / intensivity_proc, 1 / range_proc)
            processor = RequestProcessor(OA)
            model = Modeller(generator, processor)
            result_tb = model.time_based_modelling(step, time_modelling)

            p = p_teor = intensivity_gen / intensivity_proc

            self.addItemTableWidget(0, 0, round(p, 2))
            self.addItemTableWidget(0, 1, round(result_tb[5] / result_tb[6], 3))

            if 0 < p < 1:
                self.addItemTableWidget(1, 0, round(p / (1 - p) / intensivity_gen, 2))
            else:
                self.addItemTableWidget(1, 0, 6 * '*')
            self.addItemTableWidget(1, 1, round(result_tb[7], 5))

            self.addItemTableWidget(2, 0, 6 * '*')
            self.addItemTableWidget(2, 1, result_tb[0])

            self.addItemTableWidget(3, 0, 6 * '*')
            self.addItemTableWidget(3, 1, round(result_tb[3], 3))

        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setText('Произошла ошибка!\n' + repr(e))
            msgBox.show()
            msgBox.exec()

    def onGraphBtnClick(self):
        create_graph()


if __name__ == "__main__":
    app = QApplication([])
    application = mywindow()
    application.show()

    sys.exit(app.exec())
