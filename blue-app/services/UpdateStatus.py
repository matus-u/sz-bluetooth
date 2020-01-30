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

    asyncStartSignal = QtCore.pyqtSignal()
    asyncStopSignal = QtCore.pyqtSignal()
    adminModeServerRequest = QtCore.pyqtSignal()
    adminModeStateRequested = QtCore.pyqtSignal()

    newWinProbabilityValues = QtCore.pyqtSignal(object)

    def __init__(self, macAddr, moneyTracker):
        super().__init__(10000)
        self.macAddr = macAddr
        self.moneyTracker = moneyTracker
        self.moneyServer = AppSettings.actualMoneyServer()
        self.websocket = QtWebSockets.QWebSocket(parent=self)
        self.connectScheduled = True

        AppSettings.getNotifier().moneyServerChanged.connect(self.setMoneyServer)

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
        logger = LoggingService.getLogger()
        logger.info("Update state to server with id: %s" % self.URL)
        counters = self.moneyTracker.getCounters()
        data = { 'id' : self.macAddr, 'dev' : {
                "money_total" : counters[MoneyTracker.TOTAL_COUNTER_INDEX],
                "money_from_last_withdraw" : counters[MoneyTracker.FROM_LAST_WITHDRAW_COUNTER_INDEX]
                }}
        textMsg = self.createPhxMessage("update-status", data)
        LoggingService.getLogger().debug("Data to websocket %s" % textMsg)
        self.websocket.sendTextMessage(textMsg)

    def forceDisconnect(self):
        if self.websocket:
            self.websocket.abort()
            self.websocket = None
        self.scheduleConnect()

    def connect(self):
        self.ref = 0
        self.connectScheduled = False
        if self.moneyServer is not "":
            URL = self.moneyServer + "/socket/websocket"# + self.macAddr
            self.URL = URL.replace("http://", "ws://")
            LoggingService.getLogger().info("Connecting to websocket server: %s" % URL)
            self.websocket = QtWebSockets.QWebSocket(parent=self)
            self.websocket.connected.connect(self.onConnect)
            self.websocket.disconnected.connect(self.onDisconnect)
            self.websocket.textMessageReceived.connect(self.onTextMessageReceived)
            self.websocket.open(QtCore.QUrl(self.URL))
        else:
            LoggingService.getLogger().info("Stop connecting to empty websocket!")

    def onConnect(self):
        LoggingService.getLogger().info("Connected to websocket %s" % self.URL)
        self.websocket.sendTextMessage(self.createPhxMessage( "phx_join", ""));
        self.adminModeStateRequested.emit()
        self.startTimerSync()
        self.onTimeout()

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

    def onTextMessageReceived(self, js):
        LoggingService.getLogger().debug("Data from websocket %s" % js)
        text = json.loads(js)
        if text["event"] == "phx_reply" and text["payload"]["status"] == "ok" and text["ref"] != "1" and text["payload"]["response"]["msg_type"] == "update-status":
            data = text["payload"]["response"]["data"]
            AppSettings.storeServerSettings(data["name"], data["owner"], data["desc"], data["service_phone"])

        if text["event"] == "admin-mode-request":
            LoggingService.getLogger().info("Admin mode requested")
            self.adminModeServerRequest.emit()

        if text["event"] == "win-probability-settings":
            LoggingService.getLogger().info("Win probality settings: {}".format(text["payload"]))
            self.newWinProbabilityValues.emit(text["payload"])

    def onDisconnect(self):
        self.stopTimerSync()
        LoggingService.getLogger().info("Disconnected from websocket %s" % self.URL)
        self.scheduleConnect()

    def scheduleConnect(self):
        if not self.connectScheduled:
            self.connectScheduled = True
            QtCore.QTimer.singleShot(10000, self.connect)

    def createPhxMessage(self, event, payload):
        self.ref = self.ref + 1
        return json.dumps({ "topic" : "device_room:" + self.macAddr,
                            "event" : event,
                            "payload" : payload,
                            "ref" : str(self.ref)
        })
