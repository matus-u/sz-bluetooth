from PyQt5 import QtCore
from PyQt5 import QtWebSockets

from services import TimerService
from services.AppSettings import AppSettings
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker

import requests
import sys
import json

class UpdateStatus(TimerService.TimerStatusObject):

    def __init__(self, macAddr, moneyTracker):
        super().__init__(8000)
        self.macAddr = macAddr
        self.moneyTracker = moneyTracker
        self.moneyServer = AppSettings.actualMoneyServer()
        #self.start()

        AppSettings.getNotifier().moneyServerChanged.connect(self.setMoneyServer)

    def setMoneyServer(self, val):
        self.moneyServer = val

    def onTimeout(self):
        if self.moneyServer is not "":
            logger = LoggingService.getLogger()
            URL = self.moneyServer + "/api/devices/" + self.macAddr
            logger.info("Update state to server with id: %s" % URL)
            try:
                counters = self.moneyTracker.getCounters()
                data = json.dumps({ 'dev' : {
                    "money_total" : counters[MoneyTracker.TOTAL_COUNTER_INDEX],
                    "money_from_last_withdraw" : counters[MoneyTracker.FROM_LAST_WITHDRAW_COUNTER_INDEX]
                }})
                response = requests.put(URL, headers = {'Content-type': 'application/json'}, data = data, timeout = 50)
                response.raise_for_status()
                json_data = json.loads(response.text)
                AppSettings.storeServerSettings(json_data["data"]["name"], json_data["data"]["owner"], json_data["data"]["desc"], json_data["data"]["service_phone"])
                logger.info("Update state finished correctly!")
            except:
                logger.info("Update state finished with error %s" % str(sys.exc_info()[0]))

class WebSocketStatus(TimerService.TimerStatusObject):

    asyncStartSignal = QtCore.pyqtSignal()

    def __init__(self, macAddr, moneyTracker):
        super().__init__(800)
        self.macAddr = macAddr
        self.moneyTracker = moneyTracker
        self.moneyServer = AppSettings.actualMoneyServer()
        self.websocket = QtWebSockets.QWebSocket(parent=self)

        #self.start()
        AppSettings.getNotifier().moneyServerChanged.connect(self.setMoneyServer)

    def asyncStart(self):
        self.asyncStartSignal.emit()

    def afterMove(self):
        self.asyncStartSignal.connect(self.connect, QtCore.Qt.QueuedConnection)

    def setMoneyServer(self, val):
        self.moneyServer = val
        self.asyncStart()

    def onTimeout(self):
        logger = LoggingService.getLogger()
        logger.info("Update state to server with id: %s" % self.URL)
        counters = self.moneyTracker.getCounters()
        data = { 'id' : self.macAddr, 'dev' : {
                "money_total" : counters[MoneyTracker.TOTAL_COUNTER_INDEX],
                "money_from_last_withdraw" : counters[MoneyTracker.FROM_LAST_WITHDRAW_COUNTER_INDEX]
                }}
        self.websocket.sendTextMessage(self.createPhxMessage("update-status", data))

    def connect(self):
        self.ref = 0
        self.STATE = "CONNECTING"
        if self.websocket:
            self.websocket.abort()
            self.websocket = None

        if self.moneyServer is not "":
            URL = self.moneyServer + "/socket/websocket"# + self.macAddr
            self.URL = URL.replace("http://", "ws://")
            LoggingService.getLogger().info("Connecting to websocket server: %s" % URL)
            self.websocket = QtWebSockets.QWebSocket(parent=self)
            self.websocket.connected.connect(self.onConnect)
            self.websocket.disconnected.connect(self.onDisconnect)
            self.websocket.textMessageReceived.connect(self.onTextMessageReceived)
            self.websocket.open(QtCore.QUrl(self.URL))

    def onConnect(self):
        self.STATE = "CONNECTED"
        self.websocket.sendTextMessage(self.createPhxMessage( "phx_join", ""));
        self.startSync()

    def onTextMessageReceived(self, js):
        print ("ON TextMessage {}".format(js))
        text = json.loads(js)
        if text["event"] == "phx_reply" and text["payload"]["status"] == "ok" and text["ref"] != "1":
            data = text["payload"]["response"].get("data","")
            if data != "":
                AppSettings.storeServerSettings(data["name"], data["owner"], data["desc"], data["service_phone"])

    def onDisconnect(self):
        self.stopSync()
        LoggingService.getLogger().info("Disconnected from websocket %s" % self.URL)
        if self.STATE != "CONNECTED":
            self.connect()

    def createPhxMessage(self, event, payload):
        self.ref = self.ref + 1
        return json.dumps({ "topic" : "device_room:" + self.macAddr,
                            "event" : event,
                            "payload" : payload,
                            "ref" : str(self.ref)
        })
