from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os

class MusicController(QtCore.QObject):
    def __init__(self, genreWidget, songsWidget):
        super().__init__()

        self.music = {}
        self.parseMusicStorage()

        genreWidget.setRowCount(len(self.music.keys()))
        for index, item in enumerate(self.music.keys()):
            genreWidget.setItem(index,0, QtWidgets.QTableWidgetItem(item))
        genreWidget.selectRow(0);

        self.songsWidget = songsWidget
        self.genreWidget = genreWidget
        self.reloadSongsWidget()

    def parseMusicStorage(self):
        path = "/src/music"
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            path = "/media/usbstick/music"

        for item in os.listdir(path):
            subPath = os.path.join(path, item)
            if os.path.isdir(subPath):
                files = []
                for fileItem in os.listdir(subPath):
                    fileSubPath = os.path.join(subPath, fileItem)
                    if os.path.isfile(fileSubPath) and fileSubPath.endswith(".mp3"):
                        files.append(fileItem)
                self.music[item] = files


    def reloadSongsWidget(self):
        self.songsWidget.clear()
        genreKey = self.genreWidget.item(self.genreWidget.selectionModel().selectedRows()[0].row(), 0).text()
        self.songsWidget.setRowCount(len(self.music[genreKey]))
        for index, item in enumerate(self.music[genreKey]):
            self.songsWidget.setItem(index,0, QtWidgets.QTableWidgetItem(item))
        if (self.songsWidget.rowCount() > 0):
            self.songsWidget.selectRow(0)
        

    def addToPlayQueue(self):
        print ("ADD TO PLAYQUEUE")
