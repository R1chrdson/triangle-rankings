import numpy as np
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QWidget, QSlider, QFrame, QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QResizeEvent, QRegExpValidator
from .helpers import get_float


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


class BaseAlternativeWidget(QFrame):
    text_changed = pyqtSignal(QFrame)

    def __init__(self, i):
        super().__init__()
        font = QFont("MS Shell Dig 2", 14)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.i = i
        self.label = QLabel(f'a{i}')
        self.label.setFont(font)

        self.value_label = QLineEdit()
        self.value_label.setValidator(QRegExpValidator(QRegExp(r'(0([\.|,]\d{1,4})?|1([\.|,]0{1,4})?)')))
        self.value_label.setFont(font)
        self.value_label.setFixedWidth(110)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_label)

        self.value_label.editingFinished.connect(lambda: self.text_changed.emit(self))


class VisualAlternativeWidget(BaseAlternativeWidget):
    def __init__(self, i):
        super().__init__(i)
        self.slider = CustomSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.layout.insertWidget(self.layout.count() - 1, self.slider)


class VisualRankingWindow(QWidget):
    values_updated = pyqtSignal(QWidget)

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

        self.alternatives = [self.layout.itemAt(i).widget() for i in range(max_alternatives)]
        self.sliders = [a.slider for a in self.alternatives]
        self.value_labels = [a.value_label for a in self.alternatives]

        for slider in self.sliders:
            slider.valueChanged.connect(self.update_values)

        for a in self.alternatives:
            a.text_changed.connect(self.label_text)

        self.update_values()

    def label_text(self, alternative):
        n_v = round(float(alternative.value_label.text()), 4)
        other_alternatives = self.alternatives[:alternative.i] + self.alternatives[alternative.i + 1:self.size]
        other_values = np.array([a.slider.abs_value for a in other_alternatives])

        if n_v == 1.0:
            for a in self.alternatives[:self.size]:
                a.slider.abs_value = 0
                a.slider.setValue(0)
            alternative.slider.abs_value = 1.0
        else:
            if np.sum(other_values / n_v):
                alternative.slider.abs_value = round(np.sum(other_values * n_v) / (1 - n_v), 3)
            else:
                pivot = (1 - n_v) / (n_v * (self.size - 1))
                for a in self.alternatives[:self.size]:
                    a.slider.abs_value = pivot
                    a.slider.setValue(a.slider.abs_value * a.slider.width())
                alternative.slider.abs_value = 1.0

        alternative.slider.setValue(round(alternative.slider.width() * alternative.slider.abs_value))

        if alternative.slider.abs_value > 1.0:
            pivot = alternative.slider.abs_value
            for a in self.alternatives[:self.size]:
                a.slider.abs_value = a.slider.abs_value / pivot
                a.slider.setValue(a.slider.abs_value * a.slider.width())

        self.update_values()

    def update_values(self):
        values = np.array([s.abs_value for s in self.sliders[:self.size]])
        sum_values = sum(values)
        normed_values = values / sum_values if sum_values else np.ones(self.size) / self.size
        for i, value in enumerate(normed_values):
            self.value_labels[i].setText(f'{value:.4f}')

        self.values_updated.emit(self)

    def create_alternatives(self):
        for i in range(self.max_alternatives):
            self.layout.addWidget(VisualAlternativeWidget(i))

    def update_size(self, size):
        self.size = size
        for i in range(size):
            self.layout.itemAt(i).widget().show()

        for i in range(size, self.max_alternatives):
            self.layout.itemAt(i).widget().hide()

        self.update_values()


class ManualRankingWindow(QWidget):
    def __init__(self, size=10, window_title=None, max_alternatives=10):
        super().__init__()
        if window_title is not None:
            self.setWindowTitle(window_title)

        self.setFixedSize(0, 0)
        self.size = size
        self.max_alternatives = max_alternatives
        self.alternatives = []
        self.normed_values = np.ones(self.max_alternatives) / self.max_alternatives

        self.layout = QVBoxLayout()
        self.alternatives_layout = QGridLayout()
        self.layout.addLayout(self.alternatives_layout)
        self.setLayout(self.layout)
        self.create_alternatives()

        font = QFont()
        font.setPointSize(14)
        self.button = QPushButton("Update")
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button.setFont(font)
        self.layout.addWidget(self.button, alignment=Qt.AlignRight)

    def create_alternatives(self):
        for i in range(self.max_alternatives):
            alternative = BaseAlternativeWidget(i)
            alternative.text_changed.connect(self.update_normed)
            self.alternatives.append(alternative)
            self.alternatives_layout.addWidget(alternative, i // 5, i % 5)

    def update_normed(self, alternative):
        self.normed_values[alternative.i] = get_float(alternative.value_label.text())

    def update_size(self, size):
        self.size = size
        for i in range(size):
            self.alternatives_layout.itemAt(i).widget().show()

        for i in range(size, self.max_alternatives):
            self.alternatives_layout.itemAt(i).widget().hide()

        self.adjustSize()
        self.resize(0, 0)
