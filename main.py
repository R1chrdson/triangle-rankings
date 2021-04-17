import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy, QHeaderView, QTableView
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp, QAbstractTableModel, Qt, QVariant
from triangle import triangular, metric
import numpy as np


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        # return len(self._data.values)
        return 10  # Supress output and return first 10 rows

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(str(self._data.iloc[index.row()][index.column()]))
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[col])

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._data.index[col])
        return None


def get_float(string):
    if not string:
        raise ValueError('Empty value!')
    return float(string.replace(',', '.'))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.flag = True

        uic.loadUi('ui/ui/MainPage.ui', self)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.generate_button.clicked.connect(self.generate)

        edits = [self.a1_edit, self.b1_edit, self.m1_edit,
                 self.a2_edit, self.b2_edit, self.m2_edit]

        self.prev = np.array([float(edit.text()) for edit in edits])
        for edit in edits:
            edit.setValidator(QRegExpValidator(QRegExp(r'-?[0-9]+[.|,][0-9]+')))

        self.size_edit.setValidator(QIntValidator(2, 1000000))

    def generate(self):
        try:
            a1, b1, m1 = get_float(self.a1_edit.text()), get_float(self.b1_edit.text()), get_float(self.m1_edit.text())
            a2, b2, m2 = get_float(self.a2_edit.text()), get_float(self.b2_edit.text()), get_float(self.m2_edit.text())
            size = int(self.size_edit.text())
            r1 = triangular(a1, b1, m1, size)
            r2 = triangular(a2, b2, m2, size)
            current = np.array([a1, b1, m1, a2, b2, m2])

            df, metric_value, metric_rank = metric(r1, r2)

            model = PandasModel(df)
            self.table.setModel(model)
            non_zero_prev = self.prev != 0

            if (((current[non_zero_prev] / self.prev[non_zero_prev]) >= 10).any() or
                ((current[non_zero_prev] / self.prev[non_zero_prev]) <= 0.1).any() or
                self.flag):
                self.table.resizeColumnsToContents()
                self.flag = False
            self.prev = current

            self.metric_value_result.setText(str(metric_value))
            self.metric_rank_result.setText(str(metric_rank))
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(type(e).__name__)
            msg.setInformativeText(str(e))
            msg.setWindowTitle("Error")
            msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Rankings Generator")
    window.setFixedSize(767, 655)
    window.show()
    sys.exit(app.exec_())
