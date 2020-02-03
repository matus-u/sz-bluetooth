from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import deque
from mutagen.mp3 import MP3
import os

from ui import SongTableWidgetImpl

class MusicController(QtCore.QObject):

    bluetoothSelected = QtCore.pyqtSignal()

    def __init__(self, songsWidget, genreLabel):
        super().__init__()

        self.music = {}
        self.parseMusicStorage()
        self.genreLabel = genreLabel

        self.actualGenreList = list(self.music.keys())
        self.songsWidget = songsWidget
        self.reloadSongsWidget()

    def rotate(self, value):
        l = deque(self.actualGenreList)
        l.rotate(value)
        self.actualGenreList = list(l)

    def nextGenre(self):
        self.rotate(1)
        self.reloadSongsWidget()

    def previousGenre(self):
        self.rotate(-1)
        self.reloadSongsWidget()

    def getMp3Info(self, fileName, fullFileName):
        mp3 = MP3(fullFileName)
        return [fileName[:len(fileName)-4], fullFileName, mp3.info.length, False]

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
                        files.append(self.getMp3Info(fileItem, fileSubPath))
                self.music[item] = files
        self.music["Bluetooth"] = [[ "Bluetooth", "bluetooth", -1, True, lambda: self.bluetoothSelected.emit() ]]

    def reloadSongsWidget(self):
        self.genreLabel.setText(self.actualGenreList[0])
        self.songsWidget.clear()
        genreKey = self.actualGenreList[0]
        self.songsWidget.setRowCount(len(self.music[genreKey]))
        for index, item in enumerate(self.music[genreKey]):
            self.songsWidget.setCellWidget(index,0, SongTableWidgetImpl.SongTableWidgetImpl(item[0], str(int(item[2]))))
        if (self.songsWidget.rowCount() > 0):
            self.songsWidget.selectRow(0)

    def getFullSelectedMp3Info(self):
        genreKey = self.actualGenreList[0]
        if self.songsWidget.rowCount() > 0:
            if len(self.songsWidget.selectionModel().selectedRows()) > 0:
                return self.music[genreKey][self.songsWidget.selectionModel().selectedRows()[0].row()]
        return ""

