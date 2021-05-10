import sys
import numpy as np
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy, QHeaderView
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp
from utils.triangle import triangular, get_diff_ranks
from utils.pandas_table import (PandasMainTableModel, RightAlignTableModel,
                                TableWindow, AdvantagesTableModel)
from utils.set_ranking_window import ManualRankingWindow
from utils.helpers import get_float, change_visibility, get_normed
from utils.difference_search import difference_search


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initialized = False

        uic.loadUi('ui/ui/MainPage.ui', self)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.set_r1_button.hide()
        self.set_r2_button.hide()
        self.set_r1_window = ManualRankingWindow(window_title="Set R1 ranking")
        self.set_r2_window = ManualRankingWindow(window_title="Set R2 ranking")
        self.show_r1_diff_matrix_window = TableWindow("R1 diff matrix")
        self.show_r2_diff_matrix_window = TableWindow("R2 diff matrix")
        self.show_r1_diff_percent_matrix_window = TableWindow("R1 % matrix")
        self.show_r2_diff_percent_matrix_window = TableWindow("R2 % matrix")
        self.show_r1_adv_matrix_window = TableWindow("R1 K-matrix")
        self.show_r2_adv_matrix_window = TableWindow("R2 K-matrix")

        self.r1_diff_matrix_button.clicked.connect(self.show_r1_diff_matrix_window.show)
        self.r2_diff_matrix_button.clicked.connect(self.show_r2_diff_matrix_window.show)
        self.r1_diff_percent_matrix_button.clicked.connect(self.show_r1_diff_percent_matrix_window.show)
        self.r2_diff_percent_matrix_button.clicked.connect(self.show_r2_diff_percent_matrix_window.show)
        self.r1_adv_matrix_button.clicked.connect(self.show_r1_adv_matrix_window.show)
        self.r2_adv_matrix_button.clicked.connect(self.show_r2_adv_matrix_window.show)
        self.r1_diff_matrix_button.setEnabled(False)
        self.r2_diff_matrix_button.setEnabled(False)
        self.r1_diff_percent_matrix_button.setEnabled(False)
        self.r2_diff_percent_matrix_button.setEnabled(False)
        self.r1_adv_matrix_button.setEnabled(False)
        self.r2_adv_matrix_button.setEnabled(False)

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

        self.size_edit.setValidator(QIntValidator(2, 1000))
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
        self.show_r1_diff_matrix_window.close()
        self.show_r2_diff_matrix_window.close()
        self.show_r1_diff_percent_matrix_window.close()
        self.show_r2_diff_percent_matrix_window.close()
        self.show_r1_adv_matrix_window.close()
        self.show_r2_adv_matrix_window.close()

    def generate(self):
        self.update_size()
        size = int(self.size_edit.text())

        if size < 2:
            raise ValueError("Size should be > 1")

        p7, q1 = get_float(self.p7_edit.text()), get_float(self.q1_edit.text())
        if p7 + q1 > 1:
            raise ValueError("p7 + q1 should be <= 1")

        if self.r1_manual.isChecked():
            r1 = np.array([slider.abs_value for slider in self.set_r1_window.sliders[:size]])
        else:
            a1, b1, m1 = get_float(self.a1_edit.text()), get_float(self.b1_edit.text()), get_float(self.m1_edit.text())
            r1 = triangular(a1, b1, m1, size)

        if self.r2_manual.isChecked():
            r2 = np.array([slider.abs_value for slider in self.set_r2_window.sliders[:size]])
        else:
            a2, b2, m2 = get_float(self.a2_edit.text()), get_float(self.b2_edit.text()), get_float(self.m2_edit.text())
            r2 = triangular(a2, b2, m2, size)

        r1_normed = get_normed(r1)
        r2_normed = get_normed(r2)

        diff, r1_ranks, r2_ranks, diff_ranks = get_diff_ranks(r1_normed, r2_normed)
        metric = diff.sum()
        metric_rank = diff_ranks.sum()

        r1_difference_search, r2_difference_search = difference_search(r1_normed, r2_normed, p7, q1)
        r1_diff_matrix, r1_diff_percents, r1_advantages_matrix, r1_geo_mean, r1_geo_mean_normed = r1_difference_search
        r2_diff_matrix, r2_diff_percents, r2_advantages_matrix, r2_geo_mean, r2_geo_mean_normed = r2_difference_search

        data = {'R1': r1, 'R2': r2, 'R1_n': r1_normed, 'R1_Gn': r1_geo_mean_normed,
                'R2_n': r2_normed, 'R2_Gn': r2_geo_mean_normed,
                'D_n': diff, 'R1_r': r1_ranks, 'R2_r': r2_ranks, 'D_r': diff_ranks}
        df = pd.DataFrame(data=data)
        df['R1_n'] = df['R1_n'].map(lambda x: '{0:5.4f}'.format(x))
        df['R2_n'] = df['R2_n'].map(lambda x: '{0:5.4f}'.format(x))
        df['D_n'] = df['D_n'].map(lambda x: '{0:5.4f}'.format(x))
        metric_value = '{0:5.4f}'.format(metric)
        df['R1'] = df['R1'].map(lambda x: '{0:5.2f}'.format(x))
        df['R2'] = df['R2'].map(lambda x: '{0:5.2f}'.format(x))
        df['R1_Gn'] = df['R1_Gn'].map(lambda x: '{0:5.4f}'.format(x))
        df['R2_Gn'] = df['R2_Gn'].map(lambda x: '{0:5.4f}'.format(x))
        # df['|'] = ""
        # model = PandasMainTableModel(df[['R1', 'R2', '|', 'R1_n', 'R1_Gn', '|',
        #                                  'R2_n', 'R2_Gn', '|', 'D_n', 'R1_r', 'R2_r', 'D_r']])
        model = PandasMainTableModel(df)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

        r1_diff_matrix = r1_diff_matrix.applymap(lambda x: '{0:5.4f}'.format(x))
        r1_diff_model = RightAlignTableModel(r1_diff_matrix)
        self.show_r1_diff_matrix_window.setModel(r1_diff_model)

        r2_diff_matrix = r2_diff_matrix.applymap(lambda x: '{0:5.4f}'.format(x))
        r2_diff_model = RightAlignTableModel(r2_diff_matrix)
        self.show_r2_diff_matrix_window.setModel(r2_diff_model)

        r1_diff_percent_matrix = r1_diff_percents.applymap(lambda x: '{0:5.4f}'.format(x))
        r1_diff_percent_model = RightAlignTableModel(r1_diff_percent_matrix)
        self.show_r1_diff_percent_matrix_window.setModel(r1_diff_percent_model)

        r2_diff_percent_matrix = r2_diff_percents.applymap(lambda x: '{0:5.4f}'.format(x))
        r2_diff_percent_model = RightAlignTableModel(r2_diff_percent_matrix)
        self.show_r2_diff_percent_matrix_window.setModel(r2_diff_percent_model)

        r1_adv_matrix = r1_advantages_matrix.applymap(lambda x: '{0:5.2f}'.format(x))
        r1_adv_matrix['G_mean'] = r1_geo_mean.apply(lambda x: '{0:5.4f}'.format(x))
        r1_adv_model = AdvantagesTableModel(r1_adv_matrix)
        self.show_r1_adv_matrix_window.setModel(r1_adv_model)

        r2_adv_matrix = r2_advantages_matrix.applymap(lambda x: '{0:5.2f}'.format(x))
        r2_adv_matrix['G_mean'] = r2_geo_mean.apply(lambda x: '{0:5.4f}'.format(x))
        r2_adv_model = AdvantagesTableModel(r2_adv_matrix)
        self.show_r2_adv_matrix_window.setModel(r2_adv_model)

        self.metric_value_result.setText(str(metric_value))
        self.metric_rank_result.setText(str(metric_rank / 2))

        if not self.initialized:
            self.initialized = True
            self.r1_diff_matrix_button.setEnabled(True)
            self.r2_diff_matrix_button.setEnabled(True)
            self.r1_diff_percent_matrix_button.setEnabled(True)
            self.r2_diff_percent_matrix_button.setEnabled(True)
            self.r1_adv_matrix_button.setEnabled(True)
            self.r2_adv_matrix_button.setEnabled(True)


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
    window.resize(770, 770)
    window.show()
    sys.exit(app.exec_())
