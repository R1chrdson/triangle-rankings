from PyQt5.QtWidgets import QSlider


class Slider(QSlider):
    def mousePressEvent(self, e):
        self.moveByEvent(e)

    def mouseMoveEvent(self, e):
        self.moveByEvent(e)

    def moveByEvent(self, e):
        e.accept()
        x = e.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(round(value))
