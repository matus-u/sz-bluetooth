from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.MainWindow import Ui_MainWindow

from generated import Resources

import os
from services.BluetoothService import BluetoothService
from services.CreditService import CreditService
from services.AppSettings import AppSettings,AppSettingsNotifier,CoinSettingsIndexes
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
from ui import WithdrawAskWindow
from ui import WithdrawInfoWindow
from ui import DamagedDeviceWindow
from ui import TestHwWindow

from ui import LanguageSwitcher

from ui.ApplicationWindowHelpers import NotStartSameImmediatellyCheck, AppWindowArrowHandler

class ApplicationWindow(QtWidgets.QMainWindow):

    adminModeLeaveButton = QtCore.pyqtSignal()

    CONNECTION_FAILED_STR = 0
    SCANNING_STR = 1
    SECONDS = 2
    CPU_TEMP = 3
    INSERT_COIN_STRING =4
    WITHDRAW_MONEY_TEXT_HEADER =5
    WITHDRAW_MONEY_TEXT_MAIN = 6
    WITHDRAW_MONEY_TEXT_INFO_HEADER = 7
    WITHDRAW_MONEY_TEXT_INFO = 8
    SERVICE_PHONE = 9
    ADMIN_LEAVE_TXT = 10
    SONGS = 11
    PLAYING_FROM_BLUETOOTH = 12
    NOT_PLAYING = 13
    WAIT_WITH_START = 14
    ADDED_TO_QUEUE = 15
    CONNECTION_INITIALIZED = 16
    WIN_PROB_UPDATED = 17
    LOW_PAPER = 18
    CONTINUE_WITH_MUSIC = 19
    TOSS_COUNT = 20
    TOSS_MONEY_NEEDED = 21
    FIRST_TOSS_INFO = 22
    NO_PRIZES_LEFT = 23
    SCAN_AGAIN = 24
    INFO_BROWSER_TEXT = 25
    MINUTES = 26

    def createTrTexts(self):
        return {
            self.CONNECTION_FAILED_STR : self.tr("Connection with {} failed"),
            self.SCANNING_STR : self.tr("Scanninng..."),
            self.SECONDS : self.tr("seconds"),
            self.CPU_TEMP : self.tr("CPU temp: {}"),
            self.INSERT_COIN_STRING : self.tr("Insert next coin please"),
            self.WITHDRAW_MONEY_TEXT_HEADER : self.tr("Withdraw money?"),
            self.WITHDRAW_MONEY_TEXT_MAIN : self.tr("Withdraw money action requested. It will reset internal counter. Proceed?"),
            self.WITHDRAW_MONEY_TEXT_INFO_HEADER : self.tr("Withdraw succesful."),
            self.WITHDRAW_MONEY_TEXT_INFO : self.tr("Internal counter was correctly reset."),
            self.SERVICE_PHONE : self.tr("Phone to service: {}"),
            self.ADMIN_LEAVE_TXT : self.tr("Admin mode remainse for {}s"),
            self.SONGS : self.tr("songs"),
            self.PLAYING_FROM_BLUETOOTH : self.tr("Playing from bluetooth"),
            self.NOT_PLAYING : self.tr("Not playing"),
            self.WAIT_WITH_START : self.tr("Start is possible at least 5s after previous"),
            self.ADDED_TO_QUEUE : self.tr("Bluetooth will be connected at: {} "),
            self.CONNECTION_INITIALIZED : self.tr("Connecting to device: {}"),
            self.WIN_PROB_UPDATED : self.tr("Prize counts and probabilities were updated"),
            self.LOW_PAPER : self.tr("Paper will out soon, please insert new one."),
            self.CONTINUE_WITH_MUSIC : self.tr("Continue with music selection."),
            self.TOSS_COUNT : self.tr("Toss count: {}"),
            self.TOSS_MONEY_NEEDED : self.tr("To get next toss: {} {} needed"),
            self.FIRST_TOSS_INFO : self.tr("Thank you. You have got access to toss. \nSelect one song and toss will be executed."),
            self.NO_PRIZES_LEFT :  self.tr("No prizes left, only music available."),
            self.SCAN_AGAIN : self.tr("SCAN AGAIN..."),
            self.INFO_BROWSER_TEXT : self.tr("Activate funcion {} on your device. Set it to visible and press enter for network scanning."),
            self.MINUTES : self.tr("min"),
            }

    def __init__(self, timerService,
                 moneyTracker,
                 ledButtonService,
                 wheelFortuneService,
                 printingService,
                 arrowHandler,
                 errorHandler,
                 testModeService,
                 volumeService):

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
        self.temperatureStatus.actualTemperature.connect( lambda value: self.ui.cpuTempValueLabel.setText("{}".format(str(value))))
        self.ui.addCreditButton.clicked.connect(self.onAddCreditButton)
        self.ui.withdrawMoneyButton.clicked.connect(self.onWithdrawMoneyButton)
        self.ui.adminSettingsButton.clicked.connect(self.onAdminSettingsButton)
        self.ui.wifiSettingsButton.clicked.connect(lambda: self.openSubWindow(WifiSettingsWindow.WifiSettingsWindow(self, self.wirelessService)))
        self.ui.disconnectButton.clicked.connect(self.bluetoothService.asyncDisconnect)
        self.ui.leaveAdminButton.clicked.connect(lambda: self.adminModeLeaveButton.emit())
        self.texts = self.createTrTexts()

        self.creditService = CreditService(AppSettings.actualCoinSettings(), AppSettings.actualCoinLockLevel(), errorHandler, testModeService)
        self.creditService.creditChanged.connect(self.onCreditChange)
        self.creditService.moneyInserted.connect(self.moneyTracker.addToCounters)
        self.creditService.changeCredit(0)
        timerService.addTimerWorker(self.temperatureStatus)
        self.temperatureStatus.start()

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
                                                               [self.ui.leftLeftGenre, self.ui.leftGenre, self.ui.genreLabel, self.ui.rightGenre, self.ui.rightRightGenre],
                                                               self.playTrackCounter)

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.getActualFocusHandler().onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.getActualFocusHandler().onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.getActualFocusHandler().onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.getActualFocusHandler().onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.getActualFocusHandler().onConfirm())

        self.appWindowArrowHandler = AppWindowArrowHandler(self, testModeService, arrowHandler)

        self.ui.songsWidget.cellClicked.connect(lambda x,y: self.getActualFocusHandler().onConfirm())
        self.ui.playLabel.setText(self.texts[self.NOT_PLAYING])

        self.selectStackWidget(0)

        self.wheelFortuneService = wheelFortuneService
        self.ui.wheelFortuneButton.clicked.connect(lambda: self.openSubWindow(WheelSettingsWindow.WheelSettingsWindow(self, self.wheelFortuneService, self.printingService)))
        self.creditService.moneyInserted.connect(self.wheelFortuneService.moneyInserted)
        self.wheelFortuneService.fortuneDataChanged.connect(self.onFortuneDataChanged)
        self.wheelFortuneService.winCounterChanged.connect(self.onWinCounterChange)
        self.wheelFortuneService.fortuneTryFirstIncreased.connect(self.onFortuneTryFirstIncreased)

        self.wheelFortuneService.win.connect(self.onFortuneServiceTry)
        self.wheelFortuneService.probabilitiesUpdated.connect(lambda: self.showStatusInfo(4000, self.texts[self.WIN_PROB_UPDATED], self.ui.infoLabel))

        self.printingService = printingService
        printingService.lowPaper.connect(lambda: self.showError(self.texts[self.LOW_PAPER]))
        printingService.lowPaperClear.connect(lambda: self.hideError())

        self.wheelWindow = None

        self.actualTimeStampTimer = QtCore.QTimer(self)
        self.actualTimeStampTimer.timeout.connect(lambda: self.ui.actualTimeStampLabel.setText(QtCore.QTime.currentTime().toString("hh:mm")))
        self.actualTimeStampTimer.start(1000)

        QtCore.QTimer.singleShot(1000, self.onCoinImageChange)

        self.onFortuneDataChanged()
        self.noStartImmediatellyCheck = NotStartSameImmediatellyCheck()

        self.testModeService = testModeService
        self.ui.testMenuButton.clicked.connect(lambda: self.onTestMenuButton(self.printingService, self.ledButtonService, volumeService, arrowHandler))

        self.damagedDeviceWindow = DamagedDeviceWindow.DamagedDeviceWindow(self, errorHandler)
        self.damagedDeviceWindow.hidden.connect(lambda: self.getActualFocusHandler().setFocus())

        self.arrowHandler = arrowHandler
        self.ui.errorLabel.setVisible(False)

        self.languageSwitcher = LanguageSwitcher.LanguageSwitcherWidget(self)
        self.languageSwitcher.languageChanged.connect(lambda language: self.onLanguageChange(language, True))
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+x"), self, self.focusLanguageChange)

        self.musicController.bluetoothSelected.connect(self.onBluetoothGenre)
        self.musicController.bluetoothNotSelected.connect(self.onNonBluetoothGenre)

        self.onLanguageChange(AppSettings.actualLanguage())
        self.movie = QtGui.QMovie(":/images/blue-scan.gif")
        self.ui.processInfoLabel.setMovie(self.movie)
        self.movie.setScaledSize(QtCore.QSize(587,356));

        self.arrowHandler.remoteClicked.connect(self.creditService.clearCredit)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+q"), self, self.creditService.clearCredit)

    def generateInfoBrowserHtml(self):
        return """
        <html>
        <body>""" + self.texts[self.INFO_BROWSER_TEXT].format(
            "<img src=\"qrc:/images/bluetooth.png\" height=\"40\" height=\"40\" />") + """
        </body>
        </html>
        """

    def onLanguageChange(self, language, selectStackedWidget=False):
        self.languageSwitcher.setVisible(False)
        LanguageSwitcher.setLabelMovie(self.ui.languageLabel, language)
        if selectStackedWidget:
            self.selectStackWidget(self.ui.stackedWidget.currentIndex())

        styleFile = LangBasedSettings.getLangBasedQssString(language)
        styleFile.open(QtCore.QIODevice.ReadOnly)
        data = styleFile.readAll()
        self.setStyleSheet(str(data, encoding="utf-8"))

    def focusLanguageChange(self):
        if not self.languageSwitcher.isVisible():
            self.languageSwitcher.setVisible(True)
            self.languageSwitcher.move(200, 160)
            self.languageSwitcher.refresh()
            self.setActiveFocusHandler(FocusHandler.InputHandler([FocusHandler.LanguageLabelFocusProxy(self.languageSwitcher.getMainLabel(), self.ledButtonService, self.languageSwitcher)]))

    def setActiveFocusHandler(self, focusHandler):
        self.activeFocusHandler = focusHandler
        self.activeFocusHandler.setFocus()

    def selectStackWidget(self, stackIndex):
        self.ui.stackedWidget.setCurrentIndex(stackIndex)
        if stackIndex == 0:
            self.setActiveFocusHandler(FocusHandler.InputHandler([
                FocusHandler.MusicWidgetFocusProxy(self.ui.songsWidget, self.onPlaySong, self.ledButtonService, self.musicController),
                FocusHandler.SimpleInputFocusProxy(self.ui.withdrawMoneyButton, self.ledButtonService),
                FocusHandler.SimpleInputFocusProxy(self.ui.leaveAdminButton, self.ledButtonService)
            ]))
        elif stackIndex == 1:
            self.setActiveFocusHandler(FocusHandler.InputHandler([FocusHandler.TextBrowserFocusProxy(self.ui.stackedWidgetPage1, self.ledButtonService, self.musicController, self.onScan)]))
            currentCurrencyClass = AppSettings.currencyClass()
            self.ui.infoScanLabel.setText("{0} {1} = 10{2}".format(currentCurrencyClass.toString(AppSettings.actualCoinSettings()[CoinSettingsIndexes.MINUTE_COST_VALUE]*10), currentCurrencyClass.shortString(), self.texts[self.MINUTES]))
            self.ui.infoScanBrowser.setHtml(self.generateInfoBrowserHtml())
        elif stackIndex == 2:
            self.setActiveFocusHandler(FocusHandler.InputHandler([FocusHandler.FocusNullObject(self.ui.stackedWidgetPage2)]))
            self.ui.processInfoTitleLabel.setText(self.texts[self.SCANNING_STR])
            self.movie.start()

        elif stackIndex == 3:
            self.setActiveFocusHandler(FocusHandler.InputHandler([FocusHandler.TableWidgetFocusProxy(self.ui.devicesWidget, self.onConnectButton, self.ledButtonService, self.musicController)]))

    def showError(self, error):
        self.ui.errorLabel.setText(error)
        self.ui.errorLabel.setVisible(True)

    def hideError(self):
        self.ui.errorLabel.setText("")
        self.ui.errorLabel.setVisible(False)

    def getActualFocusHandler(self):
        return self.activeFocusHandler

    def onFortuneServiceTry(self, indexOfPrize, prizeName):
        w = FortuneWheelWindow.FortuneWheelWindow(self, indexOfPrize, prizeName, self.printingService, self.ledButtonService)
        self.wheelWindow = w
        w.finished.connect(lambda: self.onWheelFortuneFinished(w))
        self.openSubWindow(w)

    def onTestMenuButton(self, printerService, ledButtonService, volumeService, arrowHandler):
        self.testModeService.enableTestMode()
        w = TestHwWindow.TestHwWindow(self, printerService, ledButtonService, self.creditService.getCoinService(), volumeService, arrowHandler, self.wheelFortuneService)
        w.finished.connect(self.onTestHwWindowClosed)
        self.openSubWindow(w)

    def onTestHwWindowClosed(self):
        self.getActualFocusHandler().setFocus()
        self.testModeService.disableTestMode()

    def onWheelFortuneFinished(self, w):
        self.wheelWindow = None
        if self.wheelFortuneService.hasTries():
            self.updateWinCounterLabels()
            self.wheelFortuneService.overtakeWinTries()
        else:
            self.getActualFocusHandler().setFocus()
            self.showStatusInfo(2000, self.texts[self.CONTINUE_WITH_MUSIC], self.ui.infoLabel)
            self.onFortuneDataChanged()

    def onNonBluetoothGenre(self):
        self.selectStackWidget(0)
        self.updateCreditLabel()

    def onBluetoothGenre(self):
        self.selectStackWidget(1)
        self.updateCreditLabel()

    def onBackFromBlueButton(self):
        self.getActualFocusHandler().onLeft()
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
            self.ui.addCreditButton.setVisible(enable)
            self.ui.disconnectButton.setVisible(enable)
            self.ui.adminLeaveLabel.setVisible(enable)
            self.ui.leaveAdminButton.setVisible(enable)
            self.ui.wheelFortuneButton.setVisible(enable)
            self.ui.testMenuButton.setVisible(enable)
            if not enable:
                self.getActualFocusHandler().onLeft()
                self.getActualFocusHandler().onRight()
                self.getActualFocusHandler().setFocus()

    def openSubWindow(self, window):
        window.show()
        window.raise_()
        window.activateWindow()
        window.move(window.pos().x(), self.pos().y() + 60)

    def onSettingsFinished(self, dialogResult):
        self.creditService.setCoinSettings(AppSettings.actualCoinSettings(), AppSettings.actualCoinLockLevel())
        self.updateCreditLabel()
        self.onLanguageChange(AppSettings.actualLanguage())

        self.onFortuneDataChanged()

        if dialogResult == 1:
            self.musicController.selectModel()

    def onAdminSettingsButton(self):
        w = SettingsWindow.SettingsWindow(self, self.moneyTracker, self.wheelFortuneService, self.creditService)
        w.finished.connect(self.onSettingsFinished)
        self.openSubWindow(w)

    def cleanScannedData(self):
        self.ui.devicesWidget.clear()
        self.ui.devicesWidget.clearSelection()
        self.ui.devicesWidget.clearContents()
        self.ui.devicesWidget.setRowCount(0)

    def onScanFinished(self):
        self.scanData = self.bluetoothService.scan()
        self.ui.devicesWidget.setRowCount(len(self.scanData)+1)
        self.ui.devicesWidget.setItem(0,0, QtWidgets.QTableWidgetItem(self.texts[self.SCAN_AGAIN]))
        for index, item in enumerate(self.scanData):
            self.ui.devicesWidget.setItem(index+1,0, QtWidgets.QTableWidgetItem(str(item[0])))

        self.ui.devicesWidget.selectRow(0)
        self.selectStackWidget(3)

    def onScan(self):
        self.cleanScannedData()
        QtCore.QTimer.singleShot(3000, self.onScanFinished)
        self.selectStackWidget(2)

    def showStatusInfo(self, duration, message, label):
        label.setText(message)
        QtCore.QTimer.singleShot(duration, lambda: label.setText(""))

    def onConnectButton(self):
        if len(self.ui.devicesWidget.selectionModel().selectedRows()) > 0:
            if self.ui.devicesWidget.selectionModel().selectedRows()[0].row() == 0:
                self.onScan()
                return

        if self.creditService.getCredit() == 0.0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING], self.ui.infoLabel)
            return

        if len(self.ui.devicesWidget.selectionModel().selectedRows()) > 0:
            self.onBackFromBlueButton()
            macAddr = self.scanData[self.ui.devicesWidget.selectionModel().selectedRows()[0].row()-1][1][1:-1]
            name = self.scanData[self.ui.devicesWidget.selectionModel().selectedRows()[0].row()-1][0]
            self.ui.devicesWidget.clear()
            self.ui.devicesWidget.clearContents()
            code, startTime = self.playLogicService.play(BluetoothPlayQueueObject(name, macAddr, self.creditService.getBluetoothRepresentation().overTakeMoney()))

            if code == PlayLogicService.PLAY_RETURN_QUEUE:
                self.showStatusInfo(2000, self.texts[self.ADDED_TO_QUEUE].format(Helpers.formatStartTime(startTime)), self.ui.infoLabel)
                self.wheelFortuneService.overtakeWinTries()
            else:
                QtCore.QTimer.singleShot(2000, lambda: self.wheelFortuneService.overtakeWinTries())

    def onPlaySong(self):
        playQueueObject = self.musicController.getSelectedPlayObject()

        if (int(self.creditService.getSongsRepresentation().getCreditValueRepresentation())) <= 0:
            self.showStatusInfo(2000, self.texts[self.INSERT_COIN_STRING], self.ui.infoLabel)
            return

        if playQueueObject != None:
            if self.creditService.getSongsRepresentation().enoughMoney():
                info = playQueueObject.mp3Info()
                if not self.noStartImmediatellyCheck.check(info):
                    self.showStatusInfo(4000, self.texts[self.WAIT_WITH_START], self.ui.infoLabel)
                else:
                    self.playLogicService.play(Mp3PlayQueueObject(info))
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

    def onPlayingFailed(self, deviceName):
        self.showStatusInfo(2000, self.texts[self.CONNECTION_FAILED_STR].format(deviceName), self.ui.infoLabel)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            newTexts = self.createTrTexts()
            self.texts = newTexts
            self.ui.retranslateUi(self)
            self.updateCreditLabel()
            self.onFortuneDataChanged()
            currentCurrencyClass = AppSettings.currencyClass()
            self.ui.infoScanLabel.setText("{0} {1} = 10{2}".format(currentCurrencyClass.toString(AppSettings.actualCoinSettings()[CoinSettingsIndexes.MINUTE_COST_VALUE]*10), currentCurrencyClass.shortString(), self.texts[self.MINUTES]))
            self.ui.infoScanBrowser.setHtml(self.generateInfoBrowserHtml())
            if self.ui.errorLabel.isVisible():
                self.showError(self.texts[self.LOW_PAPER])

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
            self.ui.actualCreditValue.setText(str(self.creditService.getBluetoothRepresentation().getCreditValueRepresentation()/60) + " " + self.texts[self.MINUTES])
        currentCurrencyClass = AppSettings.currencyClass()
        self.ui.actualMoneyValue.setText(currentCurrencyClass.toString(self.creditService.getCredit()) + " " + currentCurrencyClass.longString())

    def onCreditChange(self, credit):
        self.updateCreditLabel()
        if self.creditService.getCredit() > 0:
            self.ui.infoLabel.setText("")

        if (credit > 0):
            duration = 500
            if self.playLogicService.isPlaying():
                duration = 100
            else:
                PlayWavFile(self).playWav("resources/coin-ringtone.wav")

    def onRefreshTimer(self, value):
        self.ui.playSlider.setValue(value)
        self.ui.timeLabel.setText(Helpers.formatDuration(value))

    def onAddCreditButton(self):
        value = 0.0
        values = list(filter(lambda x: (x != 0.0), self.creditService.getCoinSettings()[CoinSettingsIndexes.COIN_1:CoinSettingsIndexes.MINUTE_COST_VALUE]))
        if values:
            value = min(values)
        self.creditService.changeCredit(value)
        if not(os.getenv('RUN_FROM_DOCKER', False) == False):
            self.moneyTracker.addToCounters(value)
            self.wheelFortuneService.moneyInserted(value)

    def onWithdrawMoneyButton(self):
        self.appWindowArrowHandler.disconnectSignals()
        w = WithdrawAskWindow.WithdrawAskWindow(self, self.ledButtonService, self.arrowHandler, self.texts[self.WITHDRAW_MONEY_TEXT_MAIN], self.texts[self.WITHDRAW_MONEY_TEXT_HEADER])
        w.finished.connect(self.onWithdrawWindowFinished)
        self.openSubWindow(w)
        w.move(w.pos().x(), self.pos().y() + 150)
        w.setFocus()

    def onWithdrawWindowFinished(self, result):
        if result == QtWidgets.QDialog.Accepted:
            self.moneyTracker.withdraw()
            w = WithdrawInfoWindow.WithdrawInfoWindow(self, self.ledButtonService, self.arrowHandler, self.texts[self.WITHDRAW_MONEY_TEXT_INFO], self.texts[self.WITHDRAW_MONEY_TEXT_INFO_HEADER])
            self.openSubWindow(w)
            w.move(w.pos().x(), self.pos().y() + 150)
            w.setFocus()
            w.finished.connect(lambda: self.appWindowArrowHandler.connectSignals())
        else:
            self.appWindowArrowHandler.connectSignals()

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
            coinPixMap = LangBasedSettings.getCurrBasedCoinImage()
            self.ui.coinImgLabel.setPixmap(coinPixMap)
        QtCore.QTimer.singleShot(1000, self.onCoinImageChange)

    def updateWinCounterLabels(self):
        data = self.wheelFortuneService.getActualFortuneTryLevels()
        self.ui.actualFortuneCount.setText(self.texts[self.TOSS_COUNT].format(str(data[1])))
        self.ui.actualNeedFortuneMoney.setText(self.texts[self.TOSS_MONEY_NEEDED].format("{0:.2f}".format(data[0]), AppSettings.actualCurrency()))
        self.ui.actualFortuneCount.setVisible(True)
        self.ui.actualNeedFortuneMoney.setVisible(True)

    def onWinCounterChange(self):
        if self.wheelFortuneService.isEnabled():
            if self.wheelFortuneService.actualPrizesCount() > 0:
                self.updateWinCounterLabels()

    def onFortuneDataChanged(self):
        if self.wheelFortuneService.isEnabled():
            if self.wheelFortuneService.actualPrizesCount() > 0:
                self.updateWinCounterLabels()
            else:
                self.ui.actualFortuneCount.setText(self.texts[self.NO_PRIZES_LEFT])
                self.ui.actualFortuneCount.setVisible(True)
                self.ui.actualNeedFortuneMoney.setVisible(False)
        else:
            self.ui.actualFortuneCount.setVisible(False)
            self.ui.actualNeedFortuneMoney.setVisible(False)

    def onFortuneTryFirstIncreased(self):
        self.showStatusInfo(5000, self.texts[self.FIRST_TOSS_INFO], self.ui.infoLabel)

    def onActualServerStateChanged(self, state):
        if state == 0:
            self.ui.serverStateLabel.setText("SIDLE")

        if state == 1:
            self.ui.serverStateLabel.setText("SCETD")

        if state == 2:
            self.ui.serverStateLabel.setText("SDERR")

        if state == 3:
            self.ui.serverStateLabel.setText("SCING")
