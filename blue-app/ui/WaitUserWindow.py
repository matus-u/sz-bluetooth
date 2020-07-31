from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WaitUser import Ui_WaitUser

class WaitUserWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super(WaitUserWindow, self).__init__(parent)

        self.ui = Ui_WaitUser()
        self.ui.setupUi(self)

        self.movie = QtGui.QMovie(":/images/blue-scan.gif")
        self.ui.waitUserLabel.setMovie(self.movie)
        self.movie.setScaledSize(self.ui.waitUserLabel.size());
        #self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def paintEvent(self, event=None):
        painter = QtGui.QPainter(self)
        painter.setOpacity(0.7)
        painter.setBrush(QtCore.Qt.gray)
        painter.setPen(QtGui.QPen(QtCore.Qt.gray))
        painter.drawRect(self.rect())

    def hideWindow(self):
        self.movie.stop()
        self.hide()

    def showWindow(self):
        self.show()
        self.movie.start()
        self.movie.setScaledSize(self.ui.waitUserLabel.size());


