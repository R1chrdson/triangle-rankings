from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant


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
