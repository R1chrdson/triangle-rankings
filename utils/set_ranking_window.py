import numpy as np
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.slider import Slider


class AlternativeLayout(QFrame):
    def __init__(self, name):
        super().__init__()
        font = QFont("MS Shell Dig 2", 14)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(name)
        self.label.setFont(font)

        self.value_label = QLabel()
        self.value_label.setFont(font)
        self.value_label.setFixedWidth(76)

        self.slider = Slider(Qt.Horizontal)
        self.slider.setFixedWidth(300)
        self.slider.setRange(0, 100)
        self.slider.setPageStep(1)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setValue(50)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.value_label)


class ManualRankingWindow(QWidget):
    def __init__(self, size=10, window_title=None, max_alternatives=10):
        super().__init__()
        if window_title is not None:
            self.setWindowTitle(window_title)

        self.size = size
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.max_alternatives = max_alternatives
        self.create_alternatives()

        self.sliders = [self.layout.itemAt(i).widget().slider for i in range(max_alternatives)]
        self.value_labels = [self.layout.itemAt(i).widget().value_label for i in range(max_alternatives)]

        for slider in self.sliders:
            slider.valueChanged.connect(self.update_values)
        self.update_values()

    def update_values(self):
        values = np.array([s.value() for s in self.sliders[:self.size]])
        sum_values = sum(values)
        normed_values = values / sum_values if sum_values else np.ones(self.size) / self.size
        for i, value in enumerate(normed_values):
            self.value_labels[i].setText(f'{value:0.4f}')

    def create_alternatives(self):
        for i in range(self.max_alternatives):
            self.layout.addWidget(AlternativeLayout(f'a{i}'))

    def update_size(self, size):
        self.size = size
        for i in range(0, size):
            self.layout.itemAt(i).widget().show()

        for i in range(size, self.max_alternatives):
            self.layout.itemAt(i).widget().hide()

        self.update_values()
