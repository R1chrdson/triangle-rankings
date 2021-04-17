import sys
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp, QTimer
from utils.triangle import triangular, metric
from utils.pandas_table import PandasModel
from utils.set_ranking_window import ManualRankingWindow
from utils.helpers import get_float, change_visibility


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.flag = True

        uic.loadUi('ui/ui/MainPage.ui', self)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.set_r1_button.hide()
        self.set_r2_button.hide()
        self.set_r1_window = ManualRankingWindow(window_title="Set R1 ranking")
        self.set_r2_window = ManualRankingWindow(window_title="Set R2 ranking")

        self.generate_button.clicked.connect(self.generate)
        self.r1_automatic.toggled.connect(lambda state: change_visibility([self.a1_label, self.a1_edit,
                                                                           self.b1_label, self.b1_edit,
                                                                           self.m1_label, self.m1_edit], state))
        self.r2_automatic.toggled.connect(lambda state: change_visibility([self.a2_label, self.a2_edit,
                                                                           self.b2_label, self.b2_edit,
                                                                           self.m2_label, self.m2_edit], state))
        self.r1_manual.toggled.connect(lambda state: change_visibility([self.set_r1_button], state))
        self.r2_manual.toggled.connect(lambda state: change_visibility([self.set_r2_button], state))
        self.set_r1_button.clicked.connect(lambda: self.show_ranking_window(self.set_r1_window))
        self.set_r2_button.clicked.connect(lambda: self.show_ranking_window(self.set_r2_window))

        percent_edits = [self.p7_edit, self.q1_edit]

        for edit in percent_edits:
            edit.setValidator(QRegExpValidator(QRegExp(r'0[.|,][0-9]{2}')))

        float_edits = [self.a1_edit, self.b1_edit, self.m1_edit,
                       self.a2_edit, self.b2_edit, self.m2_edit]

        for edit in float_edits:
            edit.setValidator(QRegExpValidator(QRegExp(r'-?[0-9]{5}[.|,][0-9]{5}')))

        self.size_edit.setValidator(QIntValidator(2, 1000000))
        self.size_edit.editingFinished.connect(self.update_size)

    def show_ranking_window(self, window):
        self.update_size()
        window.show()

    def update_size(self):
        if not (self.r1_manual.isChecked() or self.r2_manual.isChecked()) or self.size_edit.hasFocus():
            return

        size = int(self.size_edit.text())
        if size > 10:
            raise ValueError("In manual mode, size can't be > 10")

        self.set_r1_window.update_size(size)
        self.set_r2_window.update_size(size)

    def closeEvent(self, event):
        self.set_r1_window.close()
        self.set_r2_window.close()

    def generate(self):
        self.update_size()
        size = int(self.size_edit.text())
        if size < 2:
            raise ValueError("Size should be > 1")

        if self.r1_manual.isChecked():
            r1 = np.array([slider.value() for slider in self.set_r1_window.sliders[:size]])
        else:
            a1, b1, m1 = get_float(self.a1_edit.text()), get_float(self.b1_edit.text()), get_float(self.m1_edit.text())
            r1 = triangular(a1, b1, m1, size)

        if self.r2_manual.isChecked():
            r2 = np.array([slider.value() for slider in self.set_r2_window.sliders[:size]])
        else:
            a2, b2, m2 = get_float(self.a2_edit.text()), get_float(self.b2_edit.text()), get_float(self.m2_edit.text())
            r2 = triangular(a2, b2, m2, size)

        df, metric_value, metric_rank = metric(r1, r2)

        model = PandasModel(df)
        self.table.setModel(model)
        # non_zero_prev = self.prev != 0

        # if (((current[non_zero_prev] / self.prev[non_zero_prev]) >= 10).any() or
        #     ((current[non_zero_prev] / self.prev[non_zero_prev]) <= 0.1).any() or
        #     self.flag):
        #     self.table.resizeColumnsToContents()
        #     self.flag = False
        # self.prev = current

        self.metric_value_result.setText(str(metric_value))
        self.metric_rank_result.setText(str(metric_rank))


def except_hook(type, value, tback):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(str(type.__name__))
    msg.setInformativeText(str(value))
    msg.setWindowTitle("Error")
    msg.exec_()
    import traceback
    print(traceback.format_exception(type, value, tback))


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Rankings Generator")
    window.setFixedSize(770, 710)
    window.show()
    sys.exit(app.exec_())
