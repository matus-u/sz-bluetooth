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

from ui import SettingsWindow
from ui import WifiSettingsWindow
from ui import MusicController
from ui import FocusHandler

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

    def createTrTexts(self):
        return [ self.tr("Time to disconnect: {}s"), self.tr("Scan bluetooth network"), self.tr("Connected to the device: "),
        self.tr("Connecting to the device: "), self.tr("Connection error"), self.tr("Connection with {} failed"), self.tr("Scanninng..."),
        self.tr("No credit"), self.tr("Zero credit, insert money first please!"), self.tr("seconds"), self.tr("CPU temp: {}"),
        self.tr("Insert next coint please"), self.tr("Withdraw money?"), self.tr("Withdraw money action requested. It will reset internal counter. Proceed?"),
        self.tr("Withdraw succesful."), self.tr("Internal counter was correctly reset."), self.tr("Phone to service: {}"), self.tr("Admin mode remainse for {}s"),
        self.tr("songs")
        ]

    def __init__(self, timerService, moneyTracker, gpioService):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.showFullScreen()
        self.moneyTracker = moneyTracker
        self.playQueue = PlayQueue()
        self.ui.playQueueWidget.setModel(self.playQueue)

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
        self.ui.connectButton.clicked.connect(self.onConnectButton)
        self.ui.disconnectButton.clicked.connect(self.bluetoothService.forceDisconnect)
        self.ui.devicesWidget.itemSelectionChanged.connect(self.onSelectionChanged)
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
        self.mainFocusHandler = FocusHandler.InputHandler(
            (FocusHandler.ButtonFocusProxy(self.ui.bluetoothButton),
             FocusHandler.GenreTableWidgetFocusProxy(self.ui.genreWidget, self.musicController),
             FocusHandler.SongTableWidgetFocusProxy(self.ui.songsWidget, self.musicController, self.playLogicService, self.creditService)))

        self.bluetoothFocusHandler = FocusHandler.InputHandler(
            (FocusHandler.ButtonFocusProxy(self.ui.scanButton),
             FocusHandler.TableWidgetFocusProxy(self.ui.devicesWidget),
             FocusHandler.ButtonFocusProxy(self.ui.backFromBlueButton),
             FocusHandler.ButtonFocusProxy(self.ui.connectButton)))

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
        self.ui.insertNewCoinLabel.setText(self.texts[self.INSERT_COIN_STRING])

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

    def onAdminSettingsButton(self):
        w = SettingsWindow.SettingsWindow(self, self.moneyTracker)
        w.finished.connect(lambda x: self.creditService.setCoinSettings(AppSettings.actualCoinSettings()))
        self.openSubWindow(w)

    def onSelectionChanged(self):
        if not self.ui.devicesWidget.selectedItems():
            self.ui.connectButton.setEnabled(False)
        else:
            self.ui.connectButton.setEnabled(True)

    def setWidgetsEnabled(self):
        self.ui.scanButton.setEnabled(True)
        self.ui.devicesWidget.setEnabled(True)

    def setWidgetsDisabled(self):
        self.ui.scanButton.setEnabled(False)
        self.ui.connectButton.setEnabled(False)
        self.ui.devicesWidget.setEnabled(False)

    def onScanButton(self):
        self.ui.devicesWidget.clear()
        self.setWidgetsDisabled()
        self.ui.scanButton.setText(self.texts[self.SCANNING_STR])
        QtCore.QCoreApplication.processEvents()
        data = self.bluetoothService.scan()
        self.ui.devicesWidget.setRowCount(len(data))
        for index, item in enumerate(data):
            self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(str(item[0])))
            self.ui.devicesWidget.setItem(index,1, QtWidgets.QTableWidgetItem(str(item[1])))

        self.setWidgetsEnabled()
        self.ui.scanButton.setText(self.texts[self.SCAN_STR])

    def onConnectButton(self):
        if self.creditService.getCredit() == 0.0:
            #QtWidgets.QMessageBox.critical(self, self.texts[self.NO_CREDIT_HEAD], self.texts[self.NO_CREDIT], QtWidgets.QMessageBox.Cancel)
            return

        self.setWidgetsDisabled() 
        macAddr = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 1).text()[1:-1]
        self.playLogicService.playFromBluetooth(macAddr, self.creditService.getBluetoothRepresentation().getCreditValueRepresentation())

    def onPlayingStarted(self):
        self.ui.playSlider.setValue(0)
        if self.playLogicService.isPlayingFromBluetooth():
            self.ui.disconnectButton.setEnabled(True)
            self.ui.playSlider.setMaximum(self.creditService.getBluetoothRepresentation().getCreditValueRepresentation())
            self.creditService.clearCredit()
            self.ui.playLabel.setText("PLAYING FROM BLUETOOTH")
        else:
            self.ui.disconnectButton.setEnabled(False)
            self.ui.playLabel.setText(self.playLogicService.getActualPlayingMp3()[0])
            self.ui.playSlider.setMaximum(self.playLogicService.getActualPlayingMp3()[2])
        self.onBackFromBlueButton()
        self.ui.bluetoothButton.setEnabled(False)

        #TODO // INFO TO ACTUAL PLAY LABELS! //

    def onPlayingStopped(self):
        #TODO CLEAR PLAY STATUS
        self.ui.playLabel.setText("NOT PLAYING")
        self.ui.devicesWidget.setRowCount(0)
        self.ui.disconnectButton.setEnabled(False)
        self.ui.bluetoothButton.setEnabled(True)
        self.ui.insertNewCoinLabel.setText(self.texts[self.INSERT_COIN_STRING])
        self.setWidgetsEnabled()

    def onPlayingFailed(self):
        deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
        QtWidgets.QMessageBox.critical(self, self.texts[self.CONNECTION_ERR_STR], self.texts[self.CONNECTION_FAILED_STR].format(deviceName), QtWidgets.QMessageBox.Cancel)
        self.setWidgetsEnabled()
        self.ui.connectButton.setEnabled(True)

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
            self.ui.actualCreditValue.setText(str(self.creditService.getSongsRepresentation().getCreditValueRepresentation()) + " " + self.texts[self.SONGS])
        else:
            self.ui.actualCreditValue.setText(str(self.creditService.getBluetoothRepresentation().getCreditValueRepresentation()) + " " + self.texts[self.SECONDS])
        self.ui.actualMoneyValue.setText(str(self.creditService.getCredit()))

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
        self.ui.timeLabel.setText(str(int(int(value)/60)) + ":" + str(value%60))

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
