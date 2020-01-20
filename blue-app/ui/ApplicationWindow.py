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
from services.PlayFileService import PlayFileService
from services.PlayLogicService import PlayLogicService
from services.MoneyTracker import MoneyTracker
from services.GpioCallback import GpioCallback

from model.PlayQueue import PlayQueue
from ui import SongTableWidgetImpl

from ui import SettingsWindow
from ui import WifiSettingsWindow
from ui import MusicController
from ui import FocusHandler
from ui import Helpers

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

    def createTrTexts(self):
        return [ self.tr("Time to disconnect: {}s"), self.tr("Scan bluetooth network"), self.tr("Connected to the device: "),
        self.tr("Connecting to the device: "), self.tr("Connection error"), self.tr("Connection with {} failed"), self.tr("Scanninng..."),
        self.tr("No credit"), self.tr("Zero credit, insert money first please!"), self.tr("seconds"), self.tr("CPU temp: {}"),
        self.tr("Insert next coin please"), self.tr("Withdraw money?"), self.tr("Withdraw money action requested. It will reset internal counter. Proceed?"),
        self.tr("Withdraw succesful."), self.tr("Internal counter was correctly reset."), self.tr("Phone to service: {}"), self.tr("Admin mode remainse for {}s"),
        self.tr("songs"), self.tr("Playing from bluetooth"), self.tr("Not playing"), self.tr("No bluetooth devices found"), self.tr("Start is possible at least 5s after previous")
        ]

    def __init__(self, timerService, moneyTracker, gpioService):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()
        self.moneyTracker = moneyTracker
        self.scanData = []

        self.playQueue = PlayQueue()
        self.playQueue.playQueueEmpty.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.playQueue.playQueueNotEmpty.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.playQueue.playQueueAdded.connect(self.onAddToPlayQueue)
        self.playQueue.playQueueRemoved.connect(self.onRemoveFromPlayQueue)
        self.ui.songsWidget.itemSelectionChanged.connect(self.onSongSelectionChanged)

        self.bluetoothService = BluetoothService(timerService)
        self.playLogicService = PlayLogicService(self.bluetoothService, self.playQueue)
        self.playLogicService.refreshTimerSignal.connect(self.onRefreshTimer)
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
        self.ui.disconnectButton.clicked.connect(self.bluetoothService.forceDisconnect)
        self.ui.leaveAdminButton.clicked.connect(lambda: self.adminModeLeaveButton.emit())
        self.texts = self.createTrTexts()

        self.creditService = CreditService(AppSettings.actualCoinSettings())
        self.creditService.creditChanged.connect(self.onCreditChange, QtCore.Qt.QueuedConnection)
        self.creditService.moneyInserted.connect(self.moneyTracker.addToCounters, QtCore.Qt.QueuedConnection)
        self.creditService.changeCredit(0)
        timerService.addTimerWorker(self.temperatureStatus)

        self.wirelessService = WirelessService()
        self.wirelessService.stateChanged.connect(self.wirelessServiceStateChanged)
        self.wirelessService.start()

        AppSettings.getNotifier().deviceNameChanged.connect(lambda val: self.ui.nameLabel.setText(val))
        AppSettings.getNotifier().servicePhoneChanged.connect(lambda val: self.ui.servicePhoneLabel.setText(self.texts[self.SERVICE_PHONE].format(val)))
        self.ui.nameLabel.setText(AppSettings.actualDeviceName())
        self.ui.servicePhoneLabel.setText(self.texts[self.SERVICE_PHONE].format(AppSettings.actualServicePhone()))

        self.musicController = MusicController.MusicController(self.ui.genreWidget, self.ui.songsWidget)
        self.ui.genreWidget.itemSelectionChanged.connect(self.onGenreConfirm)
        self.mainFocusHandler = FocusHandler.InputHandler(
            (FocusHandler.ButtonFocusProxy(self.ui.bluetoothButton),
             FocusHandler.TableWidgetFocusProxy(self.ui.genreWidget, None),
             FocusHandler.TableWidgetFocusProxy(self.ui.songsWidget, self.onPlaySong)))

        self.bluetoothFocusHandler = FocusHandler.InputHandler(
            (FocusHandler.ButtonFocusProxy(self.ui.scanButton),
             FocusHandler.TableWidgetFocusProxy(self.ui.devicesWidget, self.onConnectButton),
             FocusHandler.ButtonFocusProxy(self.ui.backFromBlueButton)))

        self.ui.backFromBlueButton.clicked.connect(self.onBackFromBlueButton)
        self.ui.bluetoothButton.clicked.connect(self.onBluetoothButton)

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.getActualFocusHandler().onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.getActualFocusHandler().onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.getActualFocusHandler().onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.getActualFocusHandler().onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.getActualFocusHandler().onConfirm())

        self.connectGpio(gpioService, 29, lambda: self.getActualFocusHandler().onLeft())
        self.connectGpio(gpioService, 31, lambda: self.getActualFocusHandler().onRight())
        self.connectGpio(gpioService, 33, lambda: self.getActualFocusHandler().onDown())
        self.connectGpio(gpioService, 35, lambda: self.getActualFocusHandler().onUp())
        self.connectGpio(gpioService, 37, lambda: self.getActualFocusHandler().onConfirm())

        self.ui.genreWidget.cellClicked.connect(lambda x,y: self.getActualFocusHandler().onConfirm())
        self.ui.songsWidget.cellClicked.connect(lambda x,y: self.getActualFocusHandler().onConfirm())
        self.ui.playLabel.setText(self.texts[self.NOT_PLAYING])

        self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()

    def connectGpio(self, gpioService, num, callback):
        gpioCall = GpioCallback(self)
        gpioCall.callbackGpio.connect(callback, QtCore.Qt.QueuedConnection)
        gpioService.registerCallback(gpioService.FALLING, num, gpioCall.onLowLevelCallback)

    def getActualFocusHandler(self):
        if self.ui.stackedWidget.currentIndex() == 0:
            return self.mainFocusHandler
        else:
            return self.bluetoothFocusHandler

    def onBluetoothButton(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.getActualFocusHandler().setFocus()
        self.updateCreditLabel()

    def onBackFromBlueButton(self):
        self.ui.stackedWidget.setCurrentIndex(0)
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
        self.creditService.setCoinSettings(AppSettings.actualCoinSettings())
        self.updateCreditLabel()

    def onAdminSettingsButton(self):
        w = SettingsWindow.SettingsWindow(self, self.moneyTracker)
        w.finished.connect(self.onSettingsFinished)
        self.openSubWindow(w)

    def setWidgetsEnabled(self):
        self.ui.scanButton.setEnabled(True)
        self.ui.devicesWidget.setEnabled(True)

    def setWidgetsDisabled(self):
        self.ui.scanButton.setEnabled(False)
        self.ui.devicesWidget.setEnabled(False)

    def onScanButton(self):
        self.ui.devicesWidget.clear()
        self.setWidgetsDisabled()
        self.ui.scanButton.setText(self.texts[self.SCANNING_STR])
        QtCore.QCoreApplication.processEvents()
        self.scanData = self.bluetoothService.scan()
        self.ui.devicesWidget.setRowCount(len(self.scanData))
        for index, item in enumerate(self.scanData):
            self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(str(item[0])))

        self.ui.scanButton.setText(self.texts[self.SCAN_STR])
        self.setWidgetsEnabled()

        if len(self.scanData) == 0:
            self.showStatusInfo(2000, self.texts[self.EMPTY_SCAN])
            self.getActualFocusHandler().setFocus()
        else:
            self.getActualFocusHandler().onLeft()

    def showStatusInfo(self, duration, message):
        self.ui.insertNewCoinLabel.setText(message)
        QtCore.QTimer.singleShot(duration, lambda: self.ui.insertNewCoinLabel.setText(""))

    def onConnectButton(self):
        if self.creditService.getCredit() == 0.0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING])
            return

        self.setWidgetsDisabled() 
        macAddr = self.scanData[self.ui.devicesWidget.selectionModel().selectedRows()[0].row()][1][1:-1]
        self.playLogicService.playFromBluetooth(macAddr, self.creditService.getBluetoothRepresentation().getCreditValueRepresentation())

    def onGenreConfirm(self):
        if self.ui.genreWidget.rowCount() > 0:
            if len(self.ui.genreWidget.selectionModel().selectedRows()) > 0:
                self.musicController.reloadSongsWidget()

    def onPlaySong(self):
        if (int(self.creditService.getSongsRepresentation().getCreditValueRepresentation())) <= 0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING])
            return
        info = self.musicController.getFullSelectedMp3Info()
        if info != "":
            if self.creditService.getSongsRepresentation().enoughMoney():
                if (QtCore.QDateTime.currentMSecsSinceEpoch() - self.lastStarted) < 0:
                    self.showStatusInfo(4000, self.texts[self.WAIT_WITH_START])
                else:
                    self.playLogicService.playFromLocal(info)
                    self.creditService.getSongsRepresentation().overTakeMoney()
                self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()


    def onPlayingStarted(self):
        self.ui.playSlider.setValue(0)
        if self.playLogicService.isPlayingFromBluetooth():
            self.ui.disconnectButton.setEnabled(True)
            self.ui.playSlider.setMaximum(self.creditService.getBluetoothRepresentation().getCreditValueRepresentation())
            self.creditService.clearCredit()
            self.ui.playLabel.setText(self.texts[self.PLAYING_FROM_BLUETOOTH])
        else:
            self.ui.disconnectButton.setEnabled(False)
            self.ui.playLabel.setText(self.playLogicService.getActualPlayingMp3()[0])
            self.ui.playSlider.setMaximum(self.playLogicService.getActualPlayingMp3()[2])
        self.onBackFromBlueButton()
        self.ui.bluetoothButton.setEnabled(False)

    def onPlayingStopped(self):
        self.ui.playLabel.setText(self.texts[self.NOT_PLAYING])
        self.ui.timeLabel.setText("")
        self.ui.playSlider.setValue(0)
        self.ui.devicesWidget.setRowCount(0)
        self.ui.disconnectButton.setEnabled(False)
        self.ui.bluetoothButton.setEnabled(True)
        self.ui.insertNewCoinLabel.setText(self.texts[self.INSERT_COIN_STRING])
        self.setWidgetsEnabled()

    def onPlayingFailed(self):
        deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
        self.showStatusInfo(2000, self.texts[self.CONNECTION_FAILED_STR].format(deviceName))
        self.setWidgetsEnabled()

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
                PlayFileService(self).playWav()
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

    def onWithdrawMoneyButton(self):
        shouldWithdraw = QtWidgets.QMessageBox.question(self, self.texts[self.WITHDRAW_MONEY_TEXT_HEADER], self.texts[self.WITHDRAW_MONEY_TEXT_MAIN])
        if shouldWithdraw == QtWidgets.QMessageBox.Yes:
            self.moneyTracker.withdraw()
            QtWidgets.QMessageBox.information(self, self.texts[self.WITHDRAW_MONEY_TEXT_INFO_HEADER], self.texts[self.WITHDRAW_MONEY_TEXT_INFO])

    def onAddToPlayQueue(self):
        count = self.playQueue.rowCount()
        self.ui.playQueueWidget.setRowCount(count)
        data = self.playQueue.data(count - 1)
        self.ui.playQueueWidget.setCellWidget(count-1, 0, SongTableWidgetImpl.SongTableWidgetImpl(data[0], data[2]))

    def onRemoveFromPlayQueue(self):
        self.ui.playQueueWidget.clear()
        count = self.playQueue.rowCount()
        self.ui.playQueueWidget.setRowCount(count)
        for i in range(0, count):
            data = self.playQueue.data(i)
            self.ui.playQueueWidget.setCellWidget(i, 0, SongTableWidgetImpl.SongTableWidgetImpl(data[0], data[2]))

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
        
