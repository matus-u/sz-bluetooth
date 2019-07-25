from PyQt5 import QtCore

class UpdateStatusThread(QtCore.QThread):

    def run(self):
        self.sendDataTimer = QtCore.QTimer()
        self.sendDataTimer.moveToThread(self)
        self.sendDataTimer.timeout.connect(self.onSendData)
        self.sendDataTimer.start(3000)
        self.exec()

    def onSendData(self):
        QtCore.QProcess.startDetached("scripts/update-state.sh")
