from PyQt5.QtWidgets import QTableView, QSizePolicy
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, pyqtSignal
from PyQt5.QtGui import QFont, QBrush


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

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


class PandasMainTableModel(PandasModel):
    def rowCount(self, parent=None):
        return min(len(self._data.values), 11)  # Suppress output and return first 10 rows

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.row() >= 10:
                    return QVariant('...')
                return QVariant(str(self._data.iloc[index.row()][index.column()]))
        return QVariant()


class AdvantagesTableModel(PandasModel):
    def rowCount(self, parent=None):
        return min(len(self._data.values), 11)  # Suppress output and return first 10 rows

    def columnCount(self, parent=None):
        return min(len(self._data.columns), 12)  # Suppress output and return first 10 columns

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.row() >= 10:
                    return QVariant('...')
                if self.columnCount() == 12:
                    if index.column() == 10:
                        return QVariant('...')
                    if index.column() == 11:
                        return QVariant(str(self._data.iloc[index.row()]['G_mean']))
                return QVariant(str(self._data.iloc[index.row(), index.column()]))
            if role == Qt.TextAlignmentRole:
                if index.row() == 10 or index.column() >= 10:
                    return int(Qt.AlignCenter)
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col >= 11:
                col = -1
            return str(self._data.columns[col])

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._data.index[col])
        return None


class RightAlignTableModel(PandasModel):
    def __init__(self, data):
        super().__init__(data)

    def rowCount(self, parent=None):
        return min(len(self._data.values), 11)  # Suppress output and return first 10 rows

    def columnCount(self, parent=None):
        return min(len(self._data.columns), 11)  # Suppress output and return first 10 columns

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.row() >= 10 or index.column() >= 10:
                    return QVariant('...')
                return QVariant(str(self._data.iloc[index.row()][index.column()]))
            if role == Qt.TextAlignmentRole:
                if index.row() >= 10 or index.column() >= 10:
                    return int(Qt.AlignCenter)
                return int(Qt.AlignRight)
        return QVariant()


class TableWindow(QTableView):
    set_model_signal = pyqtSignal()

    def __init__(self, title=None):
        super().__init__()
        if title is not None:
            self.setWindowTitle(title)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setFont(QFont("MS Shell Dig 2", 14))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.set_model_signal.connect(self.update_size)

    def setModel(self, model):
        super().setModel(model)
        self.set_model_signal.emit()

    def update_size(self):
        self.resizeColumnsToContents()
        self.setFixedSize(self.horizontalHeader().length() + self.verticalHeader().width(),
                          self.verticalHeader().length() + self.horizontalHeader().height())
