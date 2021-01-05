from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import deque
from mutagen.mp3 import MP3
import os

from ui import SongTableWidgetImpl
from services.AppSettings import AppSettings

from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject

import operator

class SongModel:
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        self.music = {}
        self.actualGenreList = []
        self.genreLabelList = genreLabelList
        self.songsWidget = songsWidget
        self.actualGenre = None
        self.playTrackCounter = playTrackCounter
        self.musicByPath = {}
        self.actualSongs = {}
        self.originalGenreLabelList = [v for v in genreLabelList]
        self.genreLabelMoving = False

    def rotate(self, value, listToRotate):
        l = deque(listToRotate)
        l.rotate(value)
        return list(l)

    def nextGenre(self):
        self.actualGenreList = self.rotate(1, self.actualGenreList)
        if self.genreLabelMoving and self.genreLabelList[2] != self.originalGenreLabelList[0]:
            self.genreLabelList = self.rotate(1, self.genreLabelList)
        self.reloadSongsWidget()

    def previousGenre(self):
        self.actualGenreList = self.rotate(-1, self.actualGenreList)
        if self.genreLabelMoving and self.genreLabelList[2] != self.originalGenreLabelList[4]:
            self.genreLabelList = self.rotate(-1, self.genreLabelList)
        self.reloadSongsWidget()

    def centerGenreLabel(self):
        self.genreLabelList = self.originalGenreLabelList
        self.reloadGenreWidgets()

    def rowCount(self):
        return len(self.actualSongs)

    def reloadGenreWidgets(self):
        for i in (0,1,3,4):
            self.genreLabelList[i].setStyleSheet("""
                background-color: rgba(0, 0, 0, 65%);
                border-top: 2px solid #ABABAB;
                border-bottom: 2px solid #ABABAB;
                font-size: 16px;
                color: white;
                """)
            self.genreLabelList[i].setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed);
            self.genreLabelList[i].setMinimumSize(0,30)
            self.genreLabelList[i].setMaximumSize(16777215,30)

        self.genreLabelList[2].setStyleSheet("""
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f70202, stop: 1 #430909);
            border: 2px solid white;
            border-radius: 15;
            font-size: 18px;
            color: white;
            """)
        self.genreLabelList[2].setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding);
        self.genreLabelList[2].setMinimumSize(0,30)
        self.genreLabelList[2].setMaximumSize(16777215,16777215)

    def reloadSongsWidget(self):
        if self.genreLabelMoving:
            self.reloadGenreWidgets()

        if self.isBluetooth():
            pix = QtGui.QPixmap(":/images/bluetooth.png")
            self.genreLabelList[2].setMinimumSize(54,54)
            self.genreLabelList[2].setMaximumSize(54,54)
            self.genreLabelList[2].setPixmap(pix.scaled(50,50))
        else:
            self.genreLabelList[2].setText(self.actualGenreList[0])
            self.genreLabelList[2].setMinimumSize(204,54)
            self.genreLabelList[2].setMaximumSize(204,54)
        self.genreLabelList[0].setText(self.actualGenreList[-2])
        self.genreLabelList[1].setText(self.actualGenreList[-1])
        self.genreLabelList[3].setText(self.actualGenreList[1])
        self.genreLabelList[4].setText(self.actualGenreList[2])
        genreKey = self.actualGenreList[0]
        self.actualGenre = genreKey
        self.actualSongs = self.music[genreKey]()
        durationVisible = AppSettings.actualSongTimeVisible()

        for index in range(0, self.songsWidget.rowCount()):
            self.songsWidget.hideRow(index)

        for index, item in enumerate(self.actualSongs):
            w = self.songsWidget.cellWidget(index,0)
            w.updateFromPlayQueueObject(item,durationVisible)
            self.songsWidget.showRow(index)

        if self.rowCount() > 0:
            self.songsWidget.selectRow(0)

    def getSelectedPlayObject(self):
        if self.rowCount() > 0:
            if len(self.songsWidget.selectionModel().selectedRows()) > 0:
                return self.actualSongs[self.songsWidget.selectionModel().selectedRows()[0].row()]
        return None

    def addSongs(self, songs):
        helpDict = {}
        for song in songs:
            selector = self.getSelector(song)
            l = helpDict.get(selector, list())
            l.append(song)
            helpDict[selector] = l
            self.musicByPath[song.path()] = song

        for key, value in helpDict.items():
            self.music[key] = lambda val=value: val

        self.generateGenreList()

    def addSpecials(self):
        self.music["Bluetooth"] = lambda : [BluetoothPlayQueueObject("Bluetooth", "", 0)]
        self.music["Top 50"] = self.generateTopTracks

    def generateTopTracks(self):
        l = list()
        for i in self.playTrackCounter.topTrackNames():
            l.append(self.musicByPath[i[0]])
        return l

    def afterModelChange(self):
        maxRowCount = len(max(self.music.items(), key=lambda x: len(x[1]()))[1]())
        self.songsWidget.clear()
        self.songsWidget.setRowCount(maxRowCount)
        for index in range(0, maxRowCount):
            self.songsWidget.setCellWidget(index,0, SongTableWidgetImpl.SongTableWidgetImpl("", BluetoothPlayQueueObject("", "", 0), True, True, self.playTrackCounter))

    def generateGenreList(self):
        self.actualGenreList = list(self.music.keys())

        if "Top 50" in self.actualGenreList:
            self.actualGenreList.remove("Top 50")
        if "Bluetooth" in self.actualGenreList:
            self.actualGenreList.remove("Bluetooth")

        self.actualGenreList.sort()
        self.actualGenreList.append("Top 50")
        self.actualGenreList.append("Bluetooth")

        if not AppSettings.actualBluetoothEnabled():
            if "Bluetooth" in self.actualGenreList:
                self.actualGenreList.remove("Bluetooth")
        if self.actualGenre in self.actualGenreList:
            self.actualGenreList = self.rotate(-1 * self.actualGenreList.index(self.actualGenre), self.actualGenreList)

    def isBluetooth(self):
        return self.actualGenreList[0] == "Bluetooth"

class GenreBasedModel(SongModel):
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__(songsWidget, genreLabelList, playTrackCounter)

    def getSelector(self, song):
        return song.genre()

class AlphaBasedModel(SongModel):
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__(songsWidget, genreLabelList, playTrackCounter)

    def getSelector(self, song):
        return song.name().lower()[0]

class MusicController(QtCore.QObject):

    bluetoothSelected = QtCore.pyqtSignal()
    bluetoothNotSelected = QtCore.pyqtSignal()

    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__()

        self.genreBasedModel = GenreBasedModel(songsWidget, genreLabelList, playTrackCounter)
        self.alphaBasedModel = AlphaBasedModel(songsWidget, genreLabelList, playTrackCounter)
        self.actualModel = None
        self.parseMusicStorage()
        self.selectModel()

    def nextGenre(self):
        self.actualModel.nextGenre()
        self.notifyBluetoothModel()

    def notifyBluetoothModel(self):
        if self.actualModel.isBluetooth():
            self.bluetoothSelected.emit()
        else:
            self.bluetoothNotSelected.emit()

    def previousGenre(self):
        self.actualModel.previousGenre()
        self.notifyBluetoothModel()

    def getMp3Info(self, fileName, fullFileName, genre):
        mp3 = MP3(fullFileName)
        return [fileName[:len(fileName)-4], fullFileName, mp3.info.length, genre]

    def parseMusicStorage(self):
        songs = []
        path = "/src/music"
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            path = "/media/usbstick/music"

        files = []
        for item in os.listdir(path):
            subPath = os.path.join(path, item)
            if os.path.isdir(subPath):
                for fileItem in os.listdir(subPath):
                    fileSubPath = os.path.join(subPath, fileItem)
                    if os.path.isfile(fileSubPath) and fileSubPath.endswith(".mp3"):
                        files.append(Mp3PlayQueueObject(self.getMp3Info(fileItem, fileSubPath, item)))

        files.sort(key=lambda x:x.path())
        self.genreBasedModel.addSongs(files)
        self.alphaBasedModel.addSongs(files)
        self.genreBasedModel.addSpecials()
        self.alphaBasedModel.addSpecials()

    def getSelectedPlayObject(self):
        return self.actualModel.getSelectedPlayObject()

    def getActualModel(self):
        if AppSettings.actualViewType() == AppSettings.ViewTypeList[1]:
            return self.alphaBasedModel
        else:
            return self.genreBasedModel

    def selectModel(self):
        self.actualModel = self.getActualModel()
        self.actualModel.afterModelChange()
        self.actualModel.generateGenreList()
        self.actualModel.genreLabelMoving = AppSettings.actualGenreIteratingType() == AppSettings.GenreIteratingList[1]
        self.actualModel.centerGenreLabel()
        self.actualModel.reloadSongsWidget()
        self.notifyBluetoothModel()

    def rowCount(self):
        return self.actualModel.rowCount()
