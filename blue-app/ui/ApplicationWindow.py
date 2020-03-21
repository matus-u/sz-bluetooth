from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.MainWindow import Ui_MainWindow

from generated import Resources

import os
from services.BluetoothService import BluetoothService
from services.CreditService import CreditService
from services.AppSettings import AppSettings,AppSettingsNotifier
from services.TemperatureStatus import TemperatureStatus
from services.WirelessService import WirelessService
from services.PlayFileService import PlayWavFile
from services.PlayLogicService import PlayLogicService
from services.PlayTrackCounter import PlayTrackCounter
from services.LangBasedSettings import LangBasedSettings

from model.PlayQueue import PlayQueue
from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject

from ui import SongTableWidgetImpl
from ui import SettingsWindow
from ui import WifiSettingsWindow
from ui import MusicController
from ui import FocusHandler
from ui import Helpers
from ui import WheelSettingsWindow
from ui import FortuneWheelWindow
from ui import DamagedDeviceWindow

class ApplicationWindow(QtWidgets.QMainWindow):

    adminModeLeaveButton = QtCore.pyqtSignal()

    DISCONNECT_STR = 0
    SCAN_STR = 1
    CONNECTED_STR = 2
    CONNECTING_STR = 3
    CONNECTION_ERR_STR = 4
    CONNECTION_FAILED_STR = 5
    SCANNING_STR = 6
    NO_CREDIT_HEAD = 7
    NO_CREDIT = 8
    SECONDS = 9
    CPU_TEMP = 10
    INSERT_COIN_STRING = 11
    WITHDRAW_MONEY_TEXT_HEADER = 12
    WITHDRAW_MONEY_TEXT_MAIN = 13
    WITHDRAW_MONEY_TEXT_INFO_HEADER = 14
    WITHDRAW_MONEY_TEXT_INFO = 15
    SERVICE_PHONE = 16
    ADMIN_LEAVE_TXT = 17
    SONGS = 18
    PLAYING_FROM_BLUETOOTH = 19
    NOT_PLAYING = 20
    EMPTY_SCAN = 21
    WAIT_WITH_START = 22
    ADDED_TO_QUEUE = 23
    CONNECTION_INITIALIZED = 24
    WIN_PROB_UPDATED = 25
    PRINT_ERROR = 26
    LOW_PAPER = 27
    NO_PAPER = 28
    CONTINUE_WITH_MUSIC = 29
    TOSS_COUNT = 30
    TOSS_MONEY_NEEDED = 31
    FIRST_TOSS_INFO = 32

    def createTrTexts(self):
        return [ self.tr("Time to disconnect: {}s"), self.tr("Scan bluetooth network"), self.tr("Connected to the device: "),
        self.tr("Connecting to the device: "), self.tr("Connection error"), self.tr("Connection with {} failed"), self.tr("Scanninng..."),
        self.tr("No credit"), self.tr("Zero credit, insert money first please!"), self.tr("seconds"), self.tr("CPU temp: {}"),
        self.tr("Insert next coin please"), self.tr("Withdraw money?"), self.tr("Withdraw money action requested. It will reset internal counter. Proceed?"),
        self.tr("Withdraw succesful."), self.tr("Internal counter was correctly reset."), self.tr("Phone to service: {}"), self.tr("Admin mode remainse for {}s"),
        self.tr("songs"), self.tr("Playing from bluetooth"), self.tr("Not playing"), self.tr("No bluetooth devices found"), self.tr("Start is possible at least 5s after previous"),
        self.tr("Bluetooth will be connected at: {} "), self.tr("Connecting to device: {}"), self.tr("Prize counts and probabilities were updated"),
        self.tr("Print error {}, call service please."), self.tr("Paper will out soon, please insert new one."), self.tr("Paper is out - please insert new one."),
        self.tr("Continue with music selection."), self.tr("Toss count: {}"), self.tr("To get next toss: {} {} needed"),
        self.tr("Thank you. You have got access to toss. \nSelect one song and toss will be executed.")
        ]

    def __init__(self, timerService, moneyTracker, ledButtonService, wheelFortuneService, printingService, arrowHandler, errorHandler):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()
        errorHandler.hwError.connect(lambda error, info: DamagedDeviceWindow.DamagedDeviceWindow(self, error).exec())
        self.moneyTracker = moneyTracker
        self.scanData = []

        self.playQueue = PlayQueue()
        self.playQueue.playQueueEmpty.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.playQueue.playQueueNotEmpty.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.playQueue.playQueueAdded.connect(self.onAddToPlayQueue)
        self.playQueue.playQueueRemoved.connect(self.onRemoveFromPlayQueue)
        self.ui.songsWidget.itemSelectionChanged.connect(self.onSongSelectionChanged)

        self.bluetoothService = BluetoothService(timerService)
        self.blueThread = QtCore.QThread(self)
        self.blueThread.start()
        self.bluetoothService.moveToThread(self.blueThread)
        self.bluetoothService.afterMove()

        self.playLogicService = PlayLogicService(self.bluetoothService, self.playQueue)
        self.playLogicService.refreshTimerSignal.connect(self.onRefreshTimer)
        self.playLogicService.playingInitialized.connect(self.onPlayingInitialized)
        self.playLogicService.playingStarted.connect(self.onPlayingStarted)
        self.playLogicService.playingStopped.connect(self.onPlayingStopped)
        self.playLogicService.playingFailed.connect(self.onPlayingFailed)

        self.temperatureStatus = TemperatureStatus()
        self.temperatureStatus.actualTemperature.connect( lambda value: self.ui.labelCpuTemp.setText(self.texts[self.CPU_TEMP].format(str(value))))
        self.ui.addCreditButton.clicked.connect(self.onAddCreditButton)
        self.ui.withdrawMoneyButton.clicked.connect(self.onWithdrawMoneyButton)
        self.ui.adminSettingsButton.clicked.connect(self.onAdminSettingsButton)
        self.ui.wifiSettingsButton.clicked.connect(lambda: self.openSubWindow(WifiSettingsWindow.WifiSettingsWindow(self, self.wirelessService)))
        self.ui.scanButton.clicked.connect(self.onScanButton)
        self.ui.disconnectButton.clicked.connect(self.bluetoothService.asyncDisconnect)
        self.ui.leaveAdminButton.clicked.connect(lambda: self.adminModeLeaveButton.emit())
        self.texts = self.createTrTexts()

        self.creditService = CreditService(AppSettings.actualCoinSettings(), AppSettings.actualCoinLockLevel(), errorHandler)
        self.creditService.creditChanged.connect(self.onCreditChange)
        self.creditService.moneyInserted.connect(self.moneyTracker.addToCounters)
        self.creditService.changeCredit(0)
        timerService.addTimerWorker(self.temperatureStatus)

        self.ledButtonService = ledButtonService
        self.ledButtonService.start()

        self.wirelessService = WirelessService()
        self.wirelessService.stateChanged.connect(self.wirelessServiceStateChanged)
        self.wirelessService.start()

        AppSettings.getNotifier().deviceNameChanged.connect(lambda val: self.ui.nameLabel.setText(val))
        AppSettings.getNotifier().servicePhoneChanged.connect(lambda val: self.ui.servicePhoneLabel.setText(self.texts[self.SERVICE_PHONE].format(val)))
        self.ui.nameLabel.setText(AppSettings.actualDeviceName())
        self.ui.servicePhoneLabel.setText(self.texts[self.SERVICE_PHONE].format(AppSettings.actualServicePhone()))

        self.playTrackCounter = PlayTrackCounter()

        self.musicController = MusicController.MusicController(self.ui.songsWidget,
                                                               [self.ui.genreLabel, self.ui.leftLeftGenre, self.ui.leftGenre, self.ui.rightGenre, self.ui.rightRightGenre],
                                                               self.playTrackCounter)
        self.mainFocusHandler = FocusHandler.InputHandler([FocusHandler.MusicWidgetFocusProxy(self.ui.songsWidget, self.onPlaySong, self.ledButtonService, self.musicController)])
        self.bluetoothFocusHandler = FocusHandler.InputHandler(
            [FocusHandler.ButtonFocusProxy(self.ui.scanButton, self.ledButtonService),
             FocusHandler.TableWidgetFocusProxy(self.ui.devicesWidget, self.onConnectButton, self.ledButtonService),
             FocusHandler.ButtonFocusProxy(self.ui.backFromBlueButton, self.ledButtonService)])

        self.ui.backFromBlueButton.clicked.connect(self.onBackFromBlueButton)

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.getActualFocusHandler().onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.getActualFocusHandler().onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.getActualFocusHandler().onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.getActualFocusHandler().onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.getActualFocusHandler().onConfirm())

        self.arrowHandler = arrowHandler
        self.arrowHandler.leftClicked.connect(lambda: self.getActualFocusHandler().onLeft())
        self.arrowHandler.rightClicked.connect(lambda: self.getActualFocusHandler().onRight())
        self.arrowHandler.downClicked.connect(lambda: self.getActualFocusHandler().onDown())
        self.arrowHandler.upClicked.connect(lambda: self.getActualFocusHandler().onUp())
        self.arrowHandler.confirmClicked.connect(lambda: self.getActualFocusHandler().onConfirm())

        self.ui.songsWidget.cellClicked.connect(lambda x,y: self.getActualFocusHandler().onConfirm())
        self.ui.playLabel.setText(self.texts[self.NOT_PLAYING])

        self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()
        self.getActualFocusHandler().setFocus()

        self.wheelFortuneService = wheelFortuneService
        self.ui.wheelFortuneButton.clicked.connect(lambda: self.openSubWindow(WheelSettingsWindow.WheelSettingsWindow(self, self.wheelFortuneService, self.printingService)))
        self.creditService.moneyInserted.connect(self.wheelFortuneService.moneyInserted)
        self.wheelFortuneService.fortuneDataChanged.connect(self.onFortuneDataChanged)
        self.wheelFortuneService.fortuneTryFirstIncreased.connect(self.onFortuneTryFirstIncreased)

        self.wheelFortuneService.win.connect(self.onFortuneServiceTry)
        self.wheelFortuneService.probabilitiesUpdated.connect(lambda: self.showStatusInfo(4000, self.texts[self.WIN_PROB_UPDATED], self.ui.infoLabel))

        self.printingService = printingService
        printingService.printError.connect(lambda: self.ui.errorLabel.setText(self.texts[self.PRINT_ERROR]).format(printingService.getErrorStatus()))
        printingService.lowPaper.connect(lambda: self.ui.errorLabel.setText(self.texts[self.LOW_PAPER]))
        printingService.noPaper.connect(lambda: self.ui.errorLabel.setText(self.texts[self.NO_PAPER]))

        self.wheelPrizes = []
        self.wheelWindow = None

        self.actualTimeStampTimer = QtCore.QTimer(self)
        self.actualTimeStampTimer.timeout.connect(lambda: self.ui.actualTimeStampLabel.setText(QtCore.QTime.currentTime().toString("hh:mm")))
        self.actualTimeStampTimer.start(1000)

        self.langBasedSettings = LangBasedSettings()
        QtCore.QTimer.singleShot(1000, self.onCoinImageChange)

        self.onFortuneDataChanged()

    def getActualFocusHandler(self):
        if self.ui.stackedWidget.currentIndex() == 0:
            return self.mainFocusHandler
        else:
            return self.bluetoothFocusHandler

    def onFortuneServiceTry(self, indexOfPrize, prizeCount, prizeName):
        self.wheelPrizes.append([indexOfPrize, prizeCount, prizeName])
        self.openFortuneWindow()

    def openFortuneWindow(self):
        if (len(self.wheelPrizes) > 0) and (self.wheelWindow is None):
            data = self.wheelPrizes.pop(0)
            w = FortuneWheelWindow.FortuneWheelWindow(self, data[0], data[1], data[2], self.printingService, self.ledButtonService, self.arrowHandler, self.langBasedSettings)
            self.wheelWindow = w
            w.finished.connect(lambda: self.onWheelFortuneFinished(w))
            self.openSubWindow(w)

    def onWheelFortuneFinished(self, w):
        self.wheelWindow = None
        if len(self.wheelPrizes):
            self.openFortuneWindow()
        else:
            self.getActualFocusHandler().setFocus()
            self.showStatusInfo(2000, self.texts[self.CONTINUE_WITH_MUSIC], self.ui.infoLabel)

    def onBluetoothGenre(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.setStyleSheet("QMainWindow { background-image: url(':/images/bg2.jpg') }");
        self.getActualFocusHandler().setFocus()
        self.updateCreditLabel()
        self.cleanScannedData()

    def onBackFromBlueButton(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.setStyleSheet("QMainWindow { background-image: url(':/images/bg.jpg') }");
        self.getActualFocusHandler().setFocus()
        self.updateCreditLabel()

    def onAdminRemaining(self, remainingTime):
        self.ui.adminLeaveLabel.setText(self.texts[self.ADMIN_LEAVE_TXT].format(str(remainingTime)))

    def onAdminMode(self, enable):
        if enable != self.ui.adminSettingsButton.isVisible():
            self.ui.adminSettingsButton.setVisible(enable)
            self.ui.wifiSettingsButton.setVisible(enable)
            self.ui.withdrawMoneyButton.setVisible(enable)
            self.ui.cpuTempValueLabel.setVisible(enable)
            self.ui.labelCpuTemp.setVisible(enable)
            self.ui.addCreditButton.setVisible(enable)
            self.ui.disconnectButton.setVisible(enable)
            self.ui.adminLeaveLabel.setVisible(enable)
            self.ui.leaveAdminButton.setVisible(enable)
            self.ui.wheelFortuneButton.setVisible(enable)
            if enable:
                self.temperatureStatus.start()
            else:
                self.temperatureStatus.stop()

    def openSubWindow(self, window):
        window.show()
        window.raise_()
        window.activateWindow()
        window.move(window.pos().x(), self.pos().y() + 60)

    def onSettingsFinished(self, x):
        self.creditService.setCoinSettings(AppSettings.actualCoinSettings(), AppSettings.actualCoinLockLevel())
        self.updateCreditLabel()
        self.langBasedSettings.reloadLanguage()
        self.onFortuneDataChanged()
        if x == 1:
            self.musicController.selectModel()

    def onAdminSettingsButton(self):
        w = SettingsWindow.SettingsWindow(self, self.moneyTracker, self.wheelFortuneService, self.creditService)
        w.finished.connect(self.onSettingsFinished)
        self.openSubWindow(w)

    def setWidgetsEnabled(self):
        self.ui.scanButton.setEnabled(True)
        self.ui.devicesWidget.setEnabled(True)
        #self.ui.backFromBlueButton.setEnabled(True)

    def setWidgetsDisabled(self):
        self.ui.scanButton.setEnabled(False)
        self.ui.devicesWidget.setEnabled(False)
        #self.ui.backFromBlueButton.setEnabled(False)

    def cleanScannedData(self):
        self.ui.devicesWidget.clear()
        self.ui.devicesWidget.clearSelection()
        self.ui.devicesWidget.clearContents()
        self.ui.devicesWidget.setRowCount(0)

    def onScanFinished(self):
        self.scanData = self.bluetoothService.scan()
        self.ui.devicesWidget.setRowCount(len(self.scanData))
        for index, item in enumerate(self.scanData):
            self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(str(item[0])))

        if len(self.scanData) > 0:
            self.ui.devicesWidget.selectRow(0)

        self.ui.scanButton.setText(self.texts[self.SCAN_STR])
        self.setWidgetsEnabled()

        if len(self.scanData) == 0:
            self.showStatusInfo(2000, self.texts[self.EMPTY_SCAN], self.ui.infoLabel)
            self.getActualFocusHandler().setFocus()
        else:
            self.getActualFocusHandler().onLeft()

    def onScanButton(self):
        self.cleanScannedData()
        self.setWidgetsDisabled()
        self.ui.scanButton.setText(self.texts[self.SCANNING_STR])
        QtCore.QCoreApplication.processEvents()
        QtCore.QTimer.singleShot(3000, self.onScanFinished)

    def showStatusInfo(self, duration, message, label):
        label.setText(message)
        QtCore.QTimer.singleShot(duration, lambda: label.setText(""))

    def onConnectButton(self):
        if self.creditService.getCredit() == 0.0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING], self.ui.insertNewCoinLabel)
            return

        if len(self.ui.devicesWidget.selectionModel().selectedRows()) > 0:
            self.onBackFromBlueButton()
            macAddr = self.scanData[self.ui.devicesWidget.selectionModel().selectedRows()[0].row()][1][1:-1]
            name = self.scanData[self.ui.devicesWidget.selectionModel().selectedRows()[0].row()][0]
            self.ui.devicesWidget.clear()
            self.ui.devicesWidget.clearContents()
            code = self.playLogicService.play(BluetoothPlayQueueObject(name, macAddr, self.creditService.getBluetoothRepresentation().getCreditValueRepresentation()))
            self.creditService.clearCredit()

            if code == PlayLogicService.PLAY_RETURN_QUEUE:
                self.showStatusInfo(2000, self.texts[self.ADDED_TO_QUEUE].format(""), self.ui.infoLabel)
                self.wheelFortuneService.overtakeWinTries()
            else:
                QtCore.QTimer.singleShot(2000, lambda: self.wheelFortuneService.overtakeWinTries())

    def onPlaySong(self):
        playQueueObject = self.musicController.getSelectedPlayObject()
        print (playQueueObject)

        #SPECIAL HANDLING OF BLUETOOTH
        if playQueueObject != None and isinstance(playQueueObject, BluetoothPlayQueueObject):
            self.onBluetoothGenre()
            return

        if (int(self.creditService.getSongsRepresentation().getCreditValueRepresentation())) <= 0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING], self.ui.insertNewCoinLabel)
            return

        if playQueueObject != None:
            if self.creditService.getSongsRepresentation().enoughMoney():
                prevLastStarted = self.lastStarted
                self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()
                if (QtCore.QDateTime.currentMSecsSinceEpoch() - prevLastStarted) < 4000:
                    self.showStatusInfo(4000, self.texts[self.WAIT_WITH_START], self.ui.infoLabel)
                else:
                    self.playLogicService.play(Mp3PlayQueueObject(playQueueObject.mp3Info()))
                    self.creditService.getSongsRepresentation().overTakeMoney()
                    self.wheelFortuneService.overtakeWinTries()


    def onPlayingInitialized(self):
        self.ui.playSlider.setValue(0)
        self.ui.playSlider.setMaximum(self.playLogicService.getActualPlayingInfo().duration())
        self.ui.totalTimeLabel.setText(Helpers.formatDuration(self.playLogicService.getActualPlayingInfo().duration()))
        if self.playLogicService.isPlayingFromBluetooth():
            self.ui.playLabel.setText(self.texts[self.CONNECTION_INITIALIZED].format(self.playLogicService.getActualPlayingInfo().name()))
        else:
            self.playTrackCounter.addToCounter(self.playLogicService.getActualPlayingInfo().path())

    def onPlayingStarted(self):
        if self.playLogicService.isPlayingFromBluetooth():
            self.ui.disconnectButton.setEnabled(True)
            self.ui.playLabel.setText(self.texts[self.PLAYING_FROM_BLUETOOTH])
        else:
            self.ui.disconnectButton.setEnabled(False)
            self.ui.playLabel.setText(self.playLogicService.getActualPlayingInfo().name())


    def onPlayingStopped(self):
        self.ui.playLabel.setText(self.texts[self.NOT_PLAYING])
        self.ui.timeLabel.setText("")
        self.ui.totalTimeLabel.setText("")
        self.ui.playSlider.setValue(0)
        self.ui.devicesWidget.setRowCount(0)
        self.ui.disconnectButton.setEnabled(False)
        self.ui.playSlider.setValue(0)
        self.ui.playSlider.setMaximum(1.0)

        #self.ui.insertNewCoinLabel.setText(self.texts[self.INSERT_COIN_STRING])

    def onPlayingFailed(self, deviceName):
        self.showStatusInfo(2000, self.texts[self.CONNECTION_FAILED_STR].format(deviceName), self.ui.infoLabel)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            newTexts = self.createTrTexts()
            if self.ui.scanButton.text() != "":
                self.ui.scanButton.setText(newTexts[self.texts.index(self.ui.scanButton.text())])
            self.texts = newTexts
            self.ui.retranslateUi(self)
        super(ApplicationWindow, self).changeEvent(event)

    def cleanup(self):
        self.creditService.cleanup()

    def wirelessServiceStateChanged(self, state, ssid):
        text = state
        if ssid != "":
            text = text + " - " + ssid
        self.ui.wifiStateLabel.setText(text)

    def updateCreditLabel(self):
        if self.ui.stackedWidget.currentIndex() == 0:
            self.ui.actualCreditValue.setText(str(int(self.creditService.getSongsRepresentation().getCreditValueRepresentation())) + " " + self.texts[self.SONGS])
        else:
            self.ui.actualCreditValue.setText(str(self.creditService.getBluetoothRepresentation().getCreditValueRepresentation()) + " " + self.texts[self.SECONDS])
        self.ui.actualMoneyValue.setText(str(self.creditService.getCredit()) + " " + AppSettings.actualCurrency())

    def onCreditChange(self, credit):
        self.updateCreditLabel()
        if self.creditService.getCredit() > 0:
            self.ui.insertNewCoinLabel.setText("")

        if (credit > 0):
            self.showCoinImage()
            duration = 500
            if self.playLogicService.isPlaying():
                duration = 100
            else:
                PlayWavFile(self).playWav("resources/coin-ringtone.wav")
            QtCore.QTimer.singleShot(duration, self.hideCoinImage)

    def onRefreshTimer(self, value):
        self.ui.playSlider.setValue(value)
        self.ui.timeLabel.setText(Helpers.formatDuration(value))

    def showCoinImage(self):
        coinPixMap = QtGui.QPixmap(':/images/coin180.png')
        self.ui.coinImageLabel.setPixmap(coinPixMap.scaled(self.ui.coinImageLabel.width(), self.ui.coinImageLabel.height()))

    def hideCoinImage(self):
        coinPixMap = QtGui.QPixmap()
        self.ui.coinImageLabel.setPixmap(coinPixMap)

    def onAddCreditButton(self):
        self.creditService.changeCredit(0.1)
        if not(os.getenv('RUN_FROM_DOCKER', False) == False):
            self.moneyTracker.addToCounters(0.1)
            self.wheelFortuneService.moneyInserted(0.1)

    def onWithdrawMoneyButton(self):
        shouldWithdraw = QtWidgets.QMessageBox.question(self, self.texts[self.WITHDRAW_MONEY_TEXT_HEADER], self.texts[self.WITHDRAW_MONEY_TEXT_MAIN])
        if shouldWithdraw == QtWidgets.QMessageBox.Yes:
            self.moneyTracker.withdraw()
            QtWidgets.QMessageBox.information(self, self.texts[self.WITHDRAW_MONEY_TEXT_INFO_HEADER], self.texts[self.WITHDRAW_MONEY_TEXT_INFO])

    def onAddToPlayQueue(self):
        self.updateTotalPlayQueueLabel()
        count = self.playQueue.rowCount()
        self.ui.playQueueWidget.setRowCount(count)
        self.ui.playQueueWidget.setCellWidget(count-1, 0, SongTableWidgetImpl.SongTableWidgetImpl.fromPlayQueueObject(self.playQueue.data(count - 1), True, True, False))

    def onRemoveFromPlayQueue(self):
        self.updateTotalPlayQueueLabel()
        self.ui.playQueueWidget.clear()
        count = self.playQueue.rowCount()
        self.ui.playQueueWidget.setRowCount(count)
        for i in range(0, count):
            self.ui.playQueueWidget.setCellWidget(i, 0, SongTableWidgetImpl.SongTableWidgetImpl.fromPlayQueueObject(self.playQueue.data(i), True, True, False))

    def onSongSelectionChanged(self):
        if self.ui.songsWidget.rowCount() > 0:
            for i in range(0, self.ui.songsWidget.rowCount()):
                widget = self.ui.songsWidget.cellWidget(i, 0)
                if widget:
                    widget.deselect()

            if len(self.ui.songsWidget.selectionModel().selectedRows()) > 0:
                row = self.ui.songsWidget.selectionModel().selectedRows()[0].row()
                widget = self.ui.songsWidget.cellWidget(row, 0)
                if widget:
                    widget.select()

    def updateTotalPlayQueueLabel(self):
        self.ui.timeOfPlayQueueLabel.setText(Helpers.formatDuration(self.playQueue.totalPlayQueueTime()))

    def onCoinImageChange(self):
        if ((self.ui.coinImgLabel.pixmap() != None) and (not self.ui.coinImgLabel.pixmap().isNull())):
            self.ui.coinImgLabel.setPixmap(QtGui.QPixmap())
        else:
            coinPixMap = self.langBasedSettings.getLangBasedCoinImage()
            self.ui.coinImgLabel.setPixmap(coinPixMap)
        QtCore.QTimer.singleShot(1000, self.onCoinImageChange)

    def onFortuneDataChanged(self):
        if self.wheelFortuneService.isEnabled():
            data = self.wheelFortuneService.getActualFortuneTryLevels()
            self.ui.actualFortuneCount.setText(self.texts[self.TOSS_COUNT].format(str(data[1])))
            self.ui.actualNeedFortuneMoney.setText(self.texts[self.TOSS_MONEY_NEEDED].format("{0:.2f}".format(data[0]), AppSettings.actualCurrency()))
            self.ui.actualFortuneCount.setVisible(True)
            self.ui.actualNeedFortuneMoney.setVisible(True)
        else:
            self.ui.actualFortuneCount.setVisible(False)
            self.ui.actualNeedFortuneMoney.setVisible(False)

    def onFortuneTryFirstIncreased(self):
        self.showStatusInfo(5000, self.texts[self.FIRST_TOSS_INFO], self.ui.infoLabel)

