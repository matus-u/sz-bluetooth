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
    def __init__(self, parent, leftLabel, rightLabel):
        super().__init__(parent)
        self.leftLabel = leftLabel
        self.rightLabel = rightLabel
        self.reloadWidgets(AppSettings.getCurrentLanguageIndex())

    def getNextLanguage(self, index):
        langList = AppSettings.LanguageList
        if index == (len(langList) -1):
            return langList[0]
        return langList[index+1]

    def getPreviousLanguage(self, index):
        langList = AppSettings.LanguageList
        if index == 0:
            return langList[len(langList) -1]
        return langList[index-1]

    def reloadWidgets(self, leftIndex):
        leftMovie = getLanguagePixmap(AppSettings.LanguageList[leftIndex])
        self.leftLabel.setMovie(leftMovie)
        leftMovie.setScaledSize(self.leftLabel.size());
        leftMovie.start()

        rightMovie = getLanguagePixmap(self.getNextLanguage(leftIndex))
        self.rightLabel.setMovie(rightMovie)
        rightMovie.setScaledSize(self.rightLabel.size());
        rightMovie.start()
