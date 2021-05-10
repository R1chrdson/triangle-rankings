import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSlider, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QResizeEvent


class CustomSlider(QSlider):
    resized = pyqtSignal(QResizeEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTickPosition(QSlider.TicksBelow)
        self.resized.connect(self.some)
        self.abs_value = .5

    def resizeEvent(self, e):
        self.resized.emit(e)
        return super().resizeEvent(e)

    def mousePressEvent(self, e):
        self.moveByEvent(e)

    def mouseMoveEvent(self, e):
        self.moveByEvent(e)

    def moveByEvent(self, e):
        e.accept()
        x = e.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.abs_value = round(value / self.width(), 3)

        if self.abs_value > 1:
            self.abs_value = 1
        elif self.abs_value < 0:
            self.abs_value = 0

        self.setValue(round(value))

    def some(self, event):
        old_width, width = event.oldSize().width(), event.size().width()
        self.setRange(0, width)
        self.setPageStep(1)
        self.setTickInterval(width / 2)
        if old_width == -1:
            self.setValue(width / 2)
        else:
            self.setValue(width * self.abs_value)


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

        self.slider = CustomSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)

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
        self.resize(1000, self.height())
        self.max_alternatives = max_alternatives
        self.create_alternatives()

        self.sliders = [self.layout.itemAt(i).widget().slider for i in range(max_alternatives)]
        self.value_labels = [self.layout.itemAt(i).widget().value_label for i in range(max_alternatives)]

        for slider in self.sliders:
            slider.valueChanged.connect(self.update_values)
        self.update_values()

    def update_values(self):
        values = np.array([s.abs_value for s in self.sliders[:self.size]])
        sum_values = sum(values)
        normed_values = values / sum_values if sum_values else np.ones(self.size) / self.size
        for i, value in enumerate(normed_values):
            self.value_labels[i].setText(f'{value:0.4f}')

    def create_alternatives(self):
        for i in range(self.max_alternatives):
            self.layout.addWidget(AlternativeLayout(f'a{i}'))

    def update_size(self, size):
        self.size = size
        for i in range(size):
            self.layout.itemAt(i).widget().show()

        for i in range(size, self.max_alternatives):
            self.layout.itemAt(i).widget().hide()

        self.update_values()
