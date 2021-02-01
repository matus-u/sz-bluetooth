from PyQt5 import QtCore
from PyQt5 import QtWebSockets
from PyQt5 import QtNetwork

from services import TimerService
from services.AppSettings import AppSettings
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker

import sys
import json

class WebSocketStatus(TimerService.TimerStatusObject):

    actualStateChanged = QtCore.pyqtSignal(int)
    asyncStartSignal = QtCore.pyqtSignal()
    asyncStopSignal = QtCore.pyqtSignal()
    adminModeServerRequest = QtCore.pyqtSignal()
    adminModeStateRequested = QtCore.pyqtSignal()
    newWinProbabilityValues = QtCore.pyqtSignal(object)
    newWinImage = QtCore.pyqtSignal(object)

    def __init__(self, macAddr, moneyTracker, wheelFortuneService, printService, errorHandler):
        super().__init__(23000)
        self.macAddr = macAddr
        self.moneyTracker = moneyTracker
        self.wheelFortuneService = wheelFortuneService
        self.moneyServer = AppSettings.actualMoneyServer()
        self.websocket = QtWebSockets.QWebSocket(parent=self)
        self.printService = printService
        self.connectScheduled = True
        self.ref = 0
        self.swVersion = AppSettings.actualAppVersion()
        self.currencyString = AppSettings.actualCurrency()
        self.errors = []
        errorHandler.hwErrorChanged.connect(self.setErrors, QtCore.Qt.QueuedConnection)
        self.updateStatusResponseWaiting = False

        AppSettings.getNotifier().moneyServerChanged.connect(self.setMoneyServer)
        AppSettings.getNotifier().currencyChanged.connect(self.setCurrency)

    def setErrors(self, errs):
        self.errors = errs

    def setCurrency(self, val):
        self.currencyString = val

    def asyncConnect(self):
        self.asyncStartSignal.emit()

    def asyncDisconnect(self):
        self.asyncStopSignal.emit()

    def afterMove(self):
        self.asyncStartSignal.connect(self.connect, QtCore.Qt.QueuedConnection)
        self.asyncStopSignal.connect(self.forceDisconnect, QtCore.Qt.QueuedConnection)

    def setMoneyServer(self, val):
        self.moneyServer = val
        self.asyncDisconnect()

    def onTimeout(self):
        if self.updateStatusResponseWaiting:
            self.updateStatusResponseWaiting = False
            self.forceDisconnect()
            LoggingService.getLogger().info("No response from server -> disconnect!")
        else:
            self.sendActualMoneyValue()
            self.sendErrorStrings()

    def sendActualMoneyValue(self):
        logger = LoggingService.getLogger()
        logger.info("Update state to server with id: %s" % self.URL)
        counters = self.moneyTracker.getCounters()
        gains = self.moneyTracker.getGainData()
        status = ""
        if len(self.errors) != 0:
            status = "ERRORS"

        data = { 'id' : self.macAddr, 'dev' : {
                "money_total" : counters[MoneyTracker.TOTAL_COUNTER_INDEX],
                "money_from_last_withdraw" : counters[MoneyTracker.FROM_LAST_WITHDRAW_COUNTER_INDEX],
                "currency" : self.currencyString,
                "version" : self.swVersion,
                "status" : status,
                "left_prizes" : self.wheelFortuneService.actualPrizesCount(),
                "last_withdraw_date" : self.moneyTracker.lastWithdrawDate(),
                "previous_gain" : gains[MoneyTracker.PreviousGain],
                "previous_gain_date" : gains[MoneyTracker.PreviousDate],
                "actual_gain" : gains[MoneyTracker.ActualGain],
                "actual_gain_date" : gains[MoneyTracker.ActualDate],
                "inkeeper_perc" : AppSettings.actualInkeeperPercentile(),
                "actual_gain_from_withdraw" : counters[MoneyTracker.ACTUAL_GAIN_FROM_LAST_WITHDRAW],
                }}
        textMsg = self.createPhxMessage("update-status", data)
        LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
        self.websocket.sendTextMessage(textMsg)
        self.updateStatusResponseWaiting = True

    def forceDisconnect(self):
        if self.websocket:
            self.websocket.abort()
            self.websocket = None
        self.scheduleConnect()

    def connect(self):
        self.ref = 0
        self.connectScheduled = False
        if self.moneyServer is not "":
            self.actualStateChanged.emit(3)
            URL = self.moneyServer + "/socket/websocket"# + self.macAddr
            self.URL = URL.replace("https://", "wss://")
            self.URL = URL.replace("http://", "ws://")
            LoggingService.getLogger().info("Connecting to websocket server: %s" % URL)
            self.websocket = QtWebSockets.QWebSocket(parent=self)
            self.websocket.connected.connect(self.onConnect)
            self.websocket.disconnected.connect(self.onDisconnect)
            self.websocket.textMessageReceived.connect(self.onTextMessageReceived)
            sslConfiguration = self.websocket.sslConfiguration()
            sslConfiguration.setPeerVerifyMode(QtNetwork.QSslSocket.VerifyNone)
            self.websocket.setSslConfiguration(sslConfiguration)
            self.websocket.ignoreSslErrors()
            self.websocket.open(QtCore.QUrl(self.URL))
        else:
            self.actualStateChanged.emit(0)
            LoggingService.getLogger().info("Stop connecting to empty websocket!")


    def onConnect(self):
        self.updateStatusResponseWaiting = False
        self.actualStateChanged.emit(1)
        LoggingService.getLogger().info("Connected to websocket %s" % self.URL)
        self.websocket.sendTextMessage(self.createPhxMessage( "phx_join", self.macAddr + "_priv", "_priv"));
        self.websocket.sendTextMessage(self.createPhxMessage( "phx_join", self.macAddr));
        self.adminModeStateRequested.emit()
        self.startTimerSync()
        self.sendActualMoneyValue()
        self.sendErrorStrings()
        self.sendWinProbsStatus()
        self.sendPrintStatus()

    def sendErrorStrings(self):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                logger = LoggingService.getLogger()
                logger.info("Send error strings:")
                data = { 'id' : self.macAddr, 'data' : { 'error-strings' : self.errors } }
                textMsg = self.createPhxMessage("error-strings", data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def sendWinProbsStatus(self):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                logger = LoggingService.getLogger()
                logger.info("Send win probs status:")
                data = { 'id' : self.macAddr, 'data' : { 'probability-data' : self.wheelFortuneService.actualProbs(),
                                                        'fortune-enabled' : self.wheelFortuneService.isEnabled()
                                                        } }
                textMsg = self.createPhxMessage("win-probability-status", data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def sendPrintStatus(self):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                logger = LoggingService.getLogger()
                logger.info("Send print status:")
                data = { 'id' : self.macAddr, 'print-status-data' : self.printService.getPrintStatus() }
                textMsg = self.createPhxMessage("print-status", data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def sendReducePrizeCount(self, prizeCountIndex):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                event = "win-probability-change"
                data = { 'id' : self.macAddr, 'index' : prizeCountIndex }
                textMsg = self.createPhxMessage(event, data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def onAdminModeLocalChange(self, enabled):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                event = "admin-mode-disabled"
                if enabled:
                    event = "admin-mode-enabled"
                data = { 'id' : self.macAddr }
                textMsg = self.createPhxMessage(event, data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def sendWinImageRequestResponse(self, image_id):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                event = "win-image-response"
                data = { 'id' : self.macAddr, 'image_id' : image_id }
                textMsg = self.createPhxMessage(event, data)
                LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
                self.websocket.sendTextMessage(textMsg)

    def onTextMessageReceived(self, js):
        LoggingService.getLogger().debug("Data from websocket %s" % js)
        text = json.loads(js)
        if text["event"] == "phx_reply" and text["payload"]["status"] == "ok" and ("msg_type" in text["payload"]["response"].keys()) and text["payload"]["response"]["msg_type"] == "update-status":
            self.updateStatusResponseWaiting = False
            data = text["payload"]["response"]["data"]
            AppSettings.storeServerSettings(data["name"], data["owner"], data["desc"], data["service_phone"])

        if text["event"] == "admin-mode-request":
            LoggingService.getLogger().info("Admin mode requested")
            self.adminModeServerRequest.emit()

        if text["event"] == "win-probability-settings":
            LoggingService.getLogger().info("Win probality settings: {}".format(text["payload"]))
            self.newWinProbabilityValues.emit(text["payload"])

        if text["event"] == "get-actual-admin-mode":
            LoggingService.getLogger().info("get-actual-admin-mode")
            self.adminModeStateRequested.emit()

        if text["event"] == "get-actual-money-value":
            LoggingService.getLogger().info("get-actual-money-value")
            self.sendActualMoneyValue()

        if text["event"] == "get-win-probability-status":
            LoggingService.getLogger().info("get-actual-prob-values")
            self.sendWinProbsStatus()

        if text["event"] == "get-print-status":
            LoggingService.getLogger().info("get-print-status")
            self.sendPrintStatus()

        if text["event"] == "win-image-request":
            LoggingService.getLogger().info("win-image-request")
            self.sendWinImageRequestResponse(text["payload"]["image_id"])
            self.newWinImage.emit(text["payload"])

        if text["event"] == "get-error-strings":
            LoggingService.getLogger().info("get-error-strings")
            self.sendErrorStrings()

    def onDisconnect(self):
        self.actualStateChanged.emit(2)
        self.stopTimerSync()
        LoggingService.getLogger().info("Disconnected from websocket %s" % self.URL)
        LoggingService.getLogger().info("Error from websocket %s" % self.websocket.errorString())
        self.scheduleConnect()

    def scheduleConnect(self):
        if not self.connectScheduled:
            self.connectScheduled = True
            QtCore.QTimer.singleShot(10000, self.connect)

    def createPhxMessage(self, event, payload, topicPriv=""):
        self.ref = self.ref + 1
        return json.dumps({ "topic" : "device_room:" + self.macAddr + topicPriv,
                            "event" : event,
                            "payload" : payload,
                            "ref" : str(self.ref)
        })
