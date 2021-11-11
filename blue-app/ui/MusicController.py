from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import deque
from mutagen.mp3 import MP3
import os

from ui import SongTableWidgetImpl
from services.AppSettings import AppSettings
from services.LoggingService import LoggingService
from services import Runnable

from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject

from services.LangBasedSettings import ThemeManager

import operator

MAX_ROW_IN_PAGE = 12

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
        self.mainLabelIndex = 2
        self.genreLabelMoving = False
        self.actualPage = 0
        self.pagesCount = 0
        self.actualPageRowCount = 0

    def rotate(self, value, listToRotate):
        l = deque(listToRotate)
        l.rotate(value)
        return list(l)

    def nextGenre(self):
        self.actualGenreList = self.rotate(1, self.actualGenreList)
        if self.genreLabelMoving and self.mainLabelIndex != 0:
            self.mainLabelIndex = self.mainLabelIndex - 1
        self.reloadSongsWidget()

    def previousGenre(self):
        self.actualGenreList = self.rotate(-1, self.actualGenreList)
        if self.genreLabelMoving and self.mainLabelIndex != 4:
            self.mainLabelIndex = self.mainLabelIndex + 1
        self.reloadSongsWidget()

    def centerGenreLabel(self):
        self.mainLabelIndex = 2
        self.reloadGenreWidgets(self.generateLabelIndexes())

    def reloadGenreWidgets(self, nonUsedIndexes):
        for i in nonUsedIndexes:
            self.genreLabelList[i].setStyleSheet(ThemeManager.inactiveGenreStyle())
            self.genreLabelList[i].setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed);
            self.genreLabelList[i].setMinimumSize(0,30)
            self.genreLabelList[i].setMaximumSize(16777215,30)

        self.genreLabelList[self.mainLabelIndex].setStyleSheet(ThemeManager.selectedGenreStyle())
        self.genreLabelList[self.mainLabelIndex].setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding);
        self.genreLabelList[self.mainLabelIndex].setMinimumSize(0,30)
        self.genreLabelList[self.mainLabelIndex].setMaximumSize(16777215,16777215)

    def generateLabelIndexes(self):
        indexes = [0,1,2,3,4]
        indexes.remove(self.mainLabelIndex)
        indexes.sort()
        return indexes

    def actualRowCount(self):
        return self.actualPageRowCount

    def _startIndexForActualPage(self):
        startIndex = self.actualPage * MAX_ROW_IN_PAGE
        if self.actualPage >= (self.pagesCount-1):
            startIndex = max(0, len(self.actualSongs) - MAX_ROW_IN_PAGE)
        return startIndex

    def reloadSongsPage(self):

        for index in range(0, self.songsWidget.rowCount()):
            self.songsWidget.hideRow(index)

        if len(self.actualSongs) == 0:
            return

        startIndex = self._startIndexForActualPage()

        counter = 0 
        durationVisible = AppSettings.actualSongTimeVisible()
        for item in self.actualSongs[startIndex:]:
            w = self.songsWidget.cellWidget(counter,0)
            w.updateFromPlayQueueObject(item,durationVisible)
            self.songsWidget.showRow(counter)
            counter = counter + 1
            startIndex = startIndex + 1

            if startIndex == len(self.actualSongs):
                break
            if counter == MAX_ROW_IN_PAGE:
                break

        self.actualPageRowCount = counter

    def reloadSongsWidget(self):

        nonUsedGenreIndexes = self.generateLabelIndexes()

        if self.genreLabelMoving:
            self.reloadGenreWidgets(nonUsedGenreIndexes)

        if self.isBluetooth():
            pix = QtGui.QPixmap(":/images/bluetooth.png")
            self.genreLabelList[self.mainLabelIndex].setMinimumSize(54,54)
            self.genreLabelList[self.mainLabelIndex].setMaximumSize(54,54)
            self.genreLabelList[self.mainLabelIndex].setPixmap(pix.scaled(50,50))
        else:
            self.genreLabelList[self.mainLabelIndex].setText(self.actualGenreList[0])
            self.genreLabelList[self.mainLabelIndex].setMinimumSize(204,54)
            self.genreLabelList[self.mainLabelIndex].setMaximumSize(204,54)

        self.genreLabelList[nonUsedGenreIndexes[0]].setText(self.actualGenreList[(0-self.mainLabelIndex + nonUsedGenreIndexes[0]) % len(self.actualGenreList)])
        self.genreLabelList[nonUsedGenreIndexes[1]].setText(self.actualGenreList[(0-self.mainLabelIndex + nonUsedGenreIndexes[1]) % len(self.actualGenreList)])
        self.genreLabelList[nonUsedGenreIndexes[2]].setText(self.actualGenreList[(0-self.mainLabelIndex + nonUsedGenreIndexes[2]) % len(self.actualGenreList)])
        self.genreLabelList[nonUsedGenreIndexes[3]].setText(self.actualGenreList[(0-self.mainLabelIndex + nonUsedGenreIndexes[3]) % len(self.actualGenreList)])

        genreKey = self.actualGenreList[0]
        self.actualGenre = genreKey
        self.actualSongs = self.music[genreKey]()

        self.pagesCount = int(len(self.actualSongs)/MAX_ROW_IN_PAGE)
        if len(self.actualSongs) % MAX_ROW_IN_PAGE > 0:
            self.pagesCount = self.pagesCount + 1

        self.actualPage = 0
        self.actualPageRowCount = 0

        self.reloadSongsPage()

        if len(self.actualSongs) > 0:
            self.songsWidget.selectRow(0)

    def getSelectedPlayObject(self):
        if self.pagesCount > 0:
            if len(self.songsWidget.selectionModel().selectedRows()) > 0:
                index = self._startIndexForActualPage() + self.songsWidget.selectionModel().selectedRows()[0].row()
                return self.actualSongs[index]
        return None

    def pageIndexUp(self):
        if self.actualPage >= (self.pagesCount-1):
            return
        self.actualPage = self.actualPage + 1
        self.reloadSongsPage()

    def pageIndexDown(self):
        if self.actualPage == 0:
            return
        self.actualPage = self.actualPage - 1
        self.reloadSongsPage()

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
            if i[0] in self.musicByPath:
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
            self.actualGenreList = self.rotate(-1 * self.actualGenreList.index(self.actualGenre), self.actualGenreList)

    def isBluetooth(self):
        return self.actualGenreList[0] == "Bluetooth"

    def afterModelChange(self):
        self.songsWidget.clear()
        self.songsWidget.setRowCount(MAX_ROW_IN_PAGE)
        for index in range(0, MAX_ROW_IN_PAGE):
            self.songsWidget.setCellWidget(index,0, SongTableWidgetImpl.SongTableWidgetImpl("", BluetoothPlayQueueObject("", "", 0), True, True, self.playTrackCounter))


class GenreBasedModel(SongModel):
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__(songsWidget, genreLabelList, playTrackCounter)

    def getSelector(self, song):
        return song.genre()

class AlphaBasedModel(SongModel):
    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__(songsWidget, genreLabelList, playTrackCounter)

    def getSelector(self, song):
        return song.name().upper()[0]

class MusicController(QtCore.QObject):

    bluetoothSelected = QtCore.pyqtSignal()
    bluetoothNotSelected = QtCore.pyqtSignal()

    def __init__(self, songsWidget, genreLabelList, playTrackCounter):
        super().__init__()

        self.genreBasedModel = GenreBasedModel(songsWidget, genreLabelList, playTrackCounter)
        self.alphaBasedModel = AlphaBasedModel(songsWidget, genreLabelList, playTrackCounter)
        self.actualModel = None

    def onInitAsync(self, initWindow):
        def asyncFunc():
            self.parseMusicStorage(initWindow)
        return Runnable.Runnable(asyncFunc)

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

    def parseMusicStorage(self, initWindow):
        songs = []
        path = "/src/music"
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            path = "/media/usbstick/music"

        initWindow.appendTextThreadSafe("Parsing started!")
        files = []
        for item in os.listdir(path):
            subPath = os.path.join(path, item)
            initWindow.appendTextThreadSafe("Parsing dir: {}".format(subPath))
            if os.path.isdir(subPath):
                for fileItem in os.listdir(subPath):
                    fileSubPath = os.path.join(subPath, fileItem)
                    #initWindow.appendTextThreadSafe("Parsing file: {}".format(fileSubPath))
                    if os.path.isfile(fileSubPath) and fileSubPath.endswith(".mp3"):
                        files.append(Mp3PlayQueueObject(self.getMp3Info(fileItem, fileSubPath, item)))

        files.sort(key=lambda x:x.path())
        self.genreBasedModel.addSongs(files)
        self.alphaBasedModel.addSongs(files)
        self.genreBasedModel.addSpecials()
        self.alphaBasedModel.addSpecials()
        initWindow.appendTextThreadSafe("Parsing finished!")

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

    def maxRowCount(self):
        return MAX_ROW_IN_PAGE

    def pageIndexUp(self):
        self.actualModel.pageIndexUp()

    def pageIndexDown(self):
        self.actualModel.pageIndexDown()

    def actualRowCount(self):
        return self.actualModel.actualRowCount()
