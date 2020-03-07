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
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        self.music = {}
        self.actualGenreList = []
        self.nonRotatedGenreList = []
        self.genreLabelList = genreLabelList
        self.songsWidget = songsWidget
        self.actualGenre = None
        self.playTrackCounter = playTrackCounter
        self.musicByPath = {}
        self.actualSongs = {}

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
        self.genreLabelList[0].setText(self.actualGenreList[0])
        self.genreLabelList[1].setText(self.actualGenreList[-2])
        self.genreLabelList[2].setText(self.actualGenreList[-1])
        self.genreLabelList[3].setText(self.actualGenreList[1])
        self.genreLabelList[4].setText(self.actualGenreList[2])
        self.songsWidget.clear()
        genreKey = self.actualGenreList[0]
        self.actualGenre = genreKey
        self.actualSongs = self.music[genreKey]()
        self.songsWidget.setRowCount(len(self.actualSongs))
        durationVisible = AppSettings.actualSongTimeVisible()
        for index, item in enumerate(self.actualSongs):
            self.songsWidget.setCellWidget(index,0, SongTableWidgetImpl.SongTableWidgetImpl.fromPlayQueueObject(item, False, durationVisible, True, self.playTrackCounter))

        if (self.songsWidget.rowCount() > 0):
            self.songsWidget.selectRow(0)

    def getSelectedPlayObject(self):
        if self.songsWidget.rowCount() > 0:
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
            self.rotate(-1 * self.actualGenreList.index(self.actualGenre))

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

    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__()

        self.genreBasedModel = GenreBasedModel(songsWidget, genreLabelList, playTrackCounter)
        self.alphaBasedModel = AlphaBasedModel(songsWidget, genreLabelList, playTrackCounter)
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
        self.genreBasedModel.addSpecials()
        self.alphaBasedModel.addSpecials()

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
        self.actualModel = self.getActualModel()
        self.actualModel.generateGenreList()
        self.actualModel.reloadSongsWidget()
