from table import ExcelTable

class PlanTableController():
    def __init__(self, filename):
        self.filename = filename


    def show(self, table):
        self.resultExcel = ExcelTable(self.filename)
        self.resultExcel.create(table)
        self.resultExcel.open()


    def addRow(self, row):
        self.resultExcel.add_one_row(row)
        self.resultExcel.open()
