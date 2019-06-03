
import sys
import webbrowser
import dbconf
import urllib.parse

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QBrush, QColor
from uimainwindow import Ui_MainWindow

SearchConceptApp = None


class DataMgr:
    def __init__(self):
        self.conn = dbconf.getconn()
        self.fetchall()

    def fetchall(self):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT `concept_id`, `concept_name`,`concept_found`,`concept_detail` FROM `search_concept`;')

        self.sdict = {}
        self.numlst = []

        for concept_id, concept_name, concept_found, concept_detail in iter(cur.fetchone, None):
            curcontent = (None, None, None)
            if concept_found is None:
                curcontent = (concept_name, Qt.white, "")
            if concept_found is 1:
                curcontent = (concept_name, Qt.blue,
                              concept_detail if concept_detail else "")
            if concept_found is 0:
                curcontent = (concept_name, Qt.red, "")
            self.sdict[concept_id] = curcontent
            self.numlst.append(concept_id)

        cur.close()

    def cols(self):
        return len(self.numlst)

    def getidbycol(self, i):
        num = self.numlst[i]
        return num

    def col(self, num):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT `concept_name`,`concept_found`,`concept_detail` FROM `search_concept` WHERE `concept_id` = ?;', (num,))
        concept_name, concept_found, concept_detail = cur.fetchone()
        cur.close()
        if concept_found is None:
            return concept_name, Qt.white, ""
        if concept_found is 1:
            return concept_name, Qt.blue, concept_detail if concept_detail else ""
        if concept_found is 0:
            return concept_name, Qt.red, ""
        return None

    def found(self, num):
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE `search_concept` SET `concept_found` = true WHERE `concept_id` = ?;', (num,))
        cur.close()
        self.conn.commit()

    def notfound(self, num):
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE `search_concept` SET `concept_found` = false WHERE `concept_id` = ?;', (num,))
        cur.close()
        self.conn.commit()

    def settext(self, num, text):
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE `search_concept` SET `concept_found` = true, `concept_detail` = ? WHERE `concept_id` = ?;', (text, num,))
        cur.close()
        self.conn.commit()

    def clear(self, num):
        self.found(num)
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE `search_concept` SET `concept_found` = NULL, `concept_detail` = NULL WHERE `concept_id` = ?;', (num,))
        cur.close()
        self.conn.commit()


class SearchTableModel(QAbstractTableModel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data

    def updaterow(self, row):
        self.dataChanged.emit(self.index(row, 0), self.index(row, 3))

    def columnCount(self, parent):
        return 3

    def rowCount(self, parent):
        return SearchConceptApp.data.cols()

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.BackgroundColorRole:
            if index.column() == 0:
                concept_id = self.data.getidbycol(index.row())
                _, clr, _ = self.data.col(concept_id)
                return QBrush(clr)
            else:
                return None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return None
            if index.column() == 1:
                concept_id = self.data.getidbycol(index.row())
                name, _, _ = self.data.col(concept_id)
                return name
            if index.column() == 2:
                return None
        return None

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ['状态', '名称', '打开浏览器'][col]
        if orientation == Qt.Vertical:
            concept_id = self.data.getidbycol(col)
            return '{}'.format(concept_id)
        return None


class SearchConcept:
    def __init__(self):
        pass

    def init(self):
        self.selection = None

        self.data = DataMgr()

        self.mainwindow = QMainWindow()
        self.uimainwindow = Ui_MainWindow()
        self.uimainwindow.setupUi(self.mainwindow)

        self.mainwindow.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.uimainwindow.found.clicked.connect(self.found)
        self.uimainwindow.notfound.clicked.connect(self.notfound)
        self.uimainwindow.save.clicked.connect(self.save)
        self.uimainwindow.clear.clicked.connect(self.clear)
        self.uimainwindow.table.clicked.connect(self.viewclicked)

        self.tablemodel = SearchTableModel(self.uimainwindow.table, self.data)
        self.uimainwindow.table.setModel(self.tablemodel)

        self.update()
        self.mainwindow.show()

    def found(self):
        if self.selection is None:
            return
        self.data.found(self.selection[0])
        self.updateselection()
        self.update()

    def notfound(self):
        if self.selection is None:
            return
        self.data.notfound(self.selection[0])
        self.updateselection()
        self.update()

    def save(self):
        if self.selection is None:
            return
        self.data.settext(self.selection[0],
                          self.uimainwindow.text.toPlainText())
        self.updateselection()
        self.update()

    def clear(self):
        if self.selection is None:
            return
        self.data.clear(self.selection[0])
        self.updateselection()
        self.update()

    def saveifchange(self):
        if self.selection is None:
            return
        if self.selection[3] != self.uimainwindow.text.toPlainText():
            self.save()

    def update(self):
        self.uimainwindow.label.setAutoFillBackground(True)

        if self.selection is None:
            self.uimainwindow.label.setText('')
            self.uimainwindow.label.setStyleSheet(
                'QLabel { background-color : white; }')
            self.uimainwindow.text.setPlainText('')
        else:
            self.uimainwindow.label.setText(self.selection[1])
            clr = QColor(self.selection[2])
            self.uimainwindow.label.setStyleSheet(
                'QLabel {{ background-color: rgb({}, {}, {}); }}'.format(
                    clr.red(), clr.green(), clr.blue()
                ))
            self.uimainwindow.text.setPlainText(self.selection[3])

    def updateselection(self):
        concept_id = self.selection[0]
        rowid = self.selection[4]
        name, clr, detail = self.data.col(concept_id)
        self.selection = (concept_id, name, clr, detail, rowid)
        self.tablemodel.updaterow(self.selection[4])

    def viewclicked(self, item):
        concept_id = self.data.getidbycol(item.row())
        name, clr, detail = self.data.col(concept_id)
        if item.column() == 2:
            url = 'https://www.google.com/search?' + \
                urllib.parse.urlencode({'q': name})
            webbrowser.open(url)
        if self.selection is None or concept_id != self.selection[0]:
            self.saveifchange()
            self.selection = (concept_id, name, clr, detail, item.row())
            self.update()


def main():
    global SearchConceptApp
    SearchConceptApp = SearchConcept()
    app = QApplication(sys.argv)
    SearchConceptApp.init()
    app.exec_()


if __name__ == '__main__':
    main()
