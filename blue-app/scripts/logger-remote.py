#!/usr/bin/python3

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtWebSockets
from PyQt5 import QtNetwork

import sys
import json
import signal
import os

class WebSocketLogService(QtCore.QObject):

    def __init__(self, macAddr):
        super().__init__()
        self.macAddr = macAddr
        self.websocket = QtWebSockets.QWebSocket(parent=self)
        self.connectScheduled = False

    def setMoneyServer(self, val):
        self.moneyServer = val
        self.forceDisconnect()

    def forceDisconnect(self):
        if self.websocket:
            self.websocket.abort()
            self.websocket = None
        self.scheduleConnect()

    def forceDisconnectStop(self):
        if self.websocket:
            self.websocket.abort()
            self.websocket = None

    def connect(self):
        self.ref = 0
        self.connectScheduled = False
        if self.moneyServer is not "":
            URL = self.moneyServer + "/socket/websocket"# + self.macAddr
            self.URL = URL.replace("http://", "ws://")
            self.websocket = QtWebSockets.QWebSocket(parent=self)
            self.websocket.connected.connect(self.onConnect)
            self.websocket.disconnected.connect(self.onDisconnect)
            self.websocket.textMessageReceived.connect(self.onTextMessageReceived)
            self.websocket.open(QtCore.QUrl(self.URL))

    def onConnect(self):
        self.websocket.sendTextMessage(self.createPhxMessage( "phx_join", self.macAddr));

    def sendLogRequest(self):
        if self.websocket is not None:
            if self.websocket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                data = { 'id' : self.macAddr, 'log-data' : self.getLogs() }
                textMsg = self.createPhxMessage("log-response", data)
                self.websocket.sendTextMessage(textMsg)

    def getLogs(self):
        #TODO LOGIC TO LOAD LOGS
        pass

    def onTextMessageReceived(self, js):
        text = json.loads(js)
        if text["event"] == "log-request":
            self.sendLogRequest()

    def onDisconnect(self):
        self.scheduleConnect()

    def scheduleConnect(self):
        if not self.connectScheduled:
            self.connectScheduled = True
            QtCore.QTimer.singleShot(5000, self.connect)

    def createPhxMessage(self, event, payload, topicPriv=""):
        self.ref = self.ref + 1
        return json.dumps({ "topic" : "device_room:" + self.macAddr + topicPriv,
                            "event" : event,
                            "payload" : payload,
                            "ref" : str(self.ref)
        })




def main():

    webSocketLogger = WebSocketLogService(sys.argv[1])
    app = QtWidgets.QApplication(sys.argv)


    def signalHandler(*args):
        with open('/tmp/money-server', 'r') as content_file:
            content = content_file.read()
            webSocketLogger.setMoneyServer(content)
        os.remove('/tmp/money-server')

    signal.signal(signal.SIGUSR1, signalHandler)

    webSocketLogger.setMoneyServer(sys.argv[2])

    timer = QtCore.QTimer()
    timer.start(500)  # You may change this if you wish.
    timer.timeout.connect(lambda: None) #let put

    ret = app.exec_()
    webSocketLogger.forceDisconnectStop()
    sys.exit(ret)

if __name__ == "__main__":
    main()
