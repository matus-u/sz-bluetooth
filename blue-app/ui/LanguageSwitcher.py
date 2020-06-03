from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.LanguageSwitcher import Ui_LanguageSwitcher

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

def setLabelMovie(label, language):
    movie = getLanguagePixmap(language)
    label.setMovie(movie)
    movie.setScaledSize(label.size());
    movie.start()

class LanguageSwitcherWidget(QtWidgets.QWidget):

    languageChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(LanguageSwitcherWidget, self).__init__(parent)
        self.ui = Ui_LanguageSwitcher()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.index = -1
        self.reloadWidgets(AppSettings.getCurrentLanguageIndex())

    def refresh(self):
        self.reloadWidgets(AppSettings.getCurrentLanguageIndex())

    def getNextLanguage(self, index):
        langList = AppSettings.actualAvailableLanguages()
        if index == (len(langList) -1):
            return langList[0]
        return langList[index+1]

    def getLanguage(self, index):
        return AppSettings.actualAvailableLanguages()[index]

    def getMainLabel(self):
        return self.ui.middleLabel

    def getPreviousLanguage(self, index):
        langList = AppSettings.actualAvailableLanguages()
        if index == 0:
            return langList[len(langList) -1]
        return langList[index-1]

    def reloadWidgets(self, middleIndex):
        setLabelMovie(self.ui.leftLabel, self.getPreviousLanguage(middleIndex))
        setLabelMovie(self.ui.middleLabel, self.getLanguage(middleIndex))
        setLabelMovie(self.ui.rightLabel, self.getNextLanguage(middleIndex))
        self.index = middleIndex

    def moveLanguageLeft(self):
        if self.index == 0:
            self.index = len(AppSettings.actualAvailableLanguages())-1
        else:
            self.index = self.index-1
        self.reloadWidgets(self.index)

    def moveLanguageRight(self):
        if self.index == (len(AppSettings.actualAvailableLanguages())-1):
            self.index = 0
        else:
            self.index = self.index + 1
        self.reloadWidgets(self.index)

    def confirmLanguageChange(self):
        language = AppSettings.actualAvailableLanguages()[self.index]
        AppSettings._loadLanguage(language)
        self.languageChanged.emit(language)
        AppSettings.storeLanguage(language)

