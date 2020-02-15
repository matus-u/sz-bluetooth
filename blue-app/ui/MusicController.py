from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import deque
from mutagen.mp3 import MP3
import os

from ui import SongTableWidgetImpl
from services.AppSettings import AppSettings

from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject

class SongModel:
    def __init__(self, songsWidget, selectedGenreWidget, playTrackCounter):
        self.music = {}
        self.actualGenreList = []
        self.nonRotatedGenreList = []
        self.genreLabel = selectedGenreWidget
        self.songsWidget = songsWidget
        self.actualGenre = None
        self.playTrackCounter = playTrackCounter

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

    def reloadSongsWidget(self):
        self.genreLabel.setText(self.actualGenreList[0])
        self.songsWidget.clear()
        genreKey = self.actualGenreList[0]
        self.actualGenre = genreKey
        self.songsWidget.setRowCount(len(self.music[genreKey]))
        durationVisible = AppSettings.actualSongTimeVisible()
        for index, item in enumerate(self.music[genreKey]):
            self.songsWidget.setCellWidget(index,0, SongTableWidgetImpl.SongTableWidgetImpl.fromPlayQueueObject(item, False, durationVisible, True, self.playTrackCounter))

        if (self.songsWidget.rowCount() > 0):
            self.songsWidget.selectRow(0)

    def getSelectedPlayObject(self):
        genreKey = self.actualGenreList[0]
        if self.songsWidget.rowCount() > 0:
            if len(self.songsWidget.selectionModel().selectedRows()) > 0:
                return self.music[genreKey][self.songsWidget.selectionModel().selectedRows()[0].row()]
        return None

    def addSongs(self, songs):
        for song in songs:
            selector = self.getSelector(song)
            l = self.music.get(selector, list())
            l.append(song)
            self.music[selector] = l
        self.generateGenreList()

    def addBluetooth(self):
        self.music["Bluetooth"] = [BluetoothPlayQueueObject("Bluetooth", "", 0)]

    def generateGenreList(self):
        self.actualGenreList = list(self.music.keys())
        if not AppSettings.actualBluetoothEnabled():
            if "Bluetooth" in self.actualGenreList:
                self.actualGenreList.remove("Bluetooth")
        if self.actualGenre in self.actualGenreList:
            self.rotate(-1 * self.actualGenreList.index(self.actualGenre))

    def label(self):
        return self.genreLabel

class GenreBasedModel(SongModel):
    def __init__(self, songsWidget, selectedGenreWidget, playTrackCounter):
        super().__init__(songsWidget, selectedGenreWidget, playTrackCounter)

    def getSelector(self, song):
        return song.genre()

class AlphaBasedModel(SongModel):
    def __init__(self, songsWidget, selectedGenreWidget, playTrackCounter):
        super().__init__(songsWidget, selectedGenreWidget, playTrackCounter)

    def getSelector(self, song):
        return song.name().lower()[0]

class MusicController(QtCore.QObject):

    bluetoothSelected = QtCore.pyqtSignal()

    def __init__(self, songsWidget, genreLabel, alphaLabel, playTrackCounter):
        super().__init__()

        self.genreBasedModel = GenreBasedModel(songsWidget, genreLabel, playTrackCounter)
        self.alphaBasedModel = AlphaBasedModel(songsWidget, alphaLabel, playTrackCounter)
        self.actualModel = None
        self.parseMusicStorage()
        self.selectModel()

    def nextGenre(self):
        self.actualModel.nextGenre()

    def previousGenre(self):
        self.actualModel.previousGenre()

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
        self.genreBasedModel.addBluetooth()
        self.alphaBasedModel.addBluetooth()

    def reloadSongsWidget(self):
        self.actualModel.reloadSongsWidget()

    def getSelectedPlayObject(self):
        return self.actualModel.getSelectedPlayObject()

    def getActualModel(self):
        if AppSettings.actualViewType() == "Alphabetical":
            return self.alphaBasedModel
        else:
            return self.genreBasedModel

    def selectModel(self):
        self.alphaBasedModel.label().hide()
        self.genreBasedModel.label().hide()
        self.actualModel = self.getActualModel()
        self.actualModel.generateGenreList()
        self.actualModel.reloadSongsWidget()
        self.actualModel.label().show()
