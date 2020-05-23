from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.Settings import Ui_Settings
from services.AppSettings import AppSettings

def getLanguagePixmap(languageString):
    if languageString == "english":
        return QtGui.QMovie(":/images/england.gif")
    if languageString == "hungarian":
        return QtGui.QMovie(":/images/hungary.gif")
    if languageString == "slovak":
        return QtGui.QMovie(":/images/slovak.gif")
    if languageString == "polish":
        return QtGui.QMovie(":/images/poland.gif")

class TempLanguageChanger(QtCore.QObject):
    languageChanged = QtCore.pyqtSignal()

    def __init__(self, parent, leftLabel, rightLabel):
        super().__init__(parent)
        self.leftLabel = leftLabel
        self.rightLabel = rightLabel
        self.index = -1
        self.reloadWidgets(AppSettings.getCurrentLanguageIndex())

    def getNextLanguage(self, index):
        langList = AppSettings.LanguageList
        if index == (len(langList) -1):
            return langList[0]
        return langList[index+1]

    def reloadWidgets(self, leftIndex):
        leftMovie = getLanguagePixmap(AppSettings.LanguageList[leftIndex])
        self.leftLabel.setMovie(leftMovie)
        leftMovie.setScaledSize(self.leftLabel.size());
        leftMovie.start()

        rightMovie = getLanguagePixmap(self.getNextLanguage(leftIndex))
        self.rightLabel.setMovie(rightMovie)
        rightMovie.setScaledSize(self.rightLabel.size());
        rightMovie.start()

        self.index = leftIndex

    def moveLanguageLeft(self):
        if self.index == 0:
            self.index = len(AppSettings.LanguageList)-1
        else:
            self.index = self.index-1
        self.reloadWidgets(self.index)

    def moveLanguageRight(self):
        if self.index == (len(AppSettings.LanguageList)-1):
            self.index = 0
        else:
            self.index = self.index + 1
        self.reloadWidgets(self.index)

    def confirmLanguageChange(self):
        AppSettings._loadLanguage(AppSettings.LanguageList[self.index])
        self.languageChanged.emit()
