# Author: Nike Liu
from PyQt5.QtCore import Qt,QAbstractTableModel

class DataFrameTableModel(QAbstractTableModel):
    """将DataFrame 转成 TableModel"""
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.colors = dict()

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role= Qt.DisplayRole):
        """ return dataframe single data with a location"""
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
            if role == Qt.BackgroundRole:
                color = self.colors.get((index.row(), index.column()))
                if color is not None:
                    return color
        return None

        # return QAbstractTableModel.data(self, index, role)

    def headerData(self, rowcol, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        """复选框使用？通过Delegate创建QCheckBox来实现的Check列"""
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[Ncol], ascending=not order)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

    def change_color(self, row, column, color):
        ix = self.index(row, column)
        self.colors[(row, column)] = color
        self.dataChanged.emit(ix, ix, (Qt.BackgroundRole,))

    # def setFrontColor(self,index,column):
    #     self.itemData(index=index).set

class pandasModel(QAbstractTableModel):

    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

        self.colors = dict()

    def rowCount(self, parent=None):
        return self._data.index.size

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
            # 居中对齐
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            # 设置单元格底色
            # if role == Qt.BackgroundRole:
            #     color = self.colors.get((index.row(), index.column()))
            #     if color is not None:
            #         return color
            # 设置单元格字体颜色
            if role == Qt.TextColorRole:  # 设置字体颜色
                color = self.colors.get((index.row(), index.column()))
                if color is not None:
                    return color

        return None

    def headerData(self, rowcol, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(
                self._data.columns[Ncol], ascending=not order
            )
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

    def change_color(self, row, column, color):
        ix = self.index(row, column)
        self.colors[(row, column)] = color
        self.dataChanged.emit(ix, ix, (Qt.TextColorRole,))