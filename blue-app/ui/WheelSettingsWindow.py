from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.WheelSettings import Ui_WheelSettings
from services.WheelFortuneService import WheelFortuneService
from services.AppSettings import AppSettings

class WheelSettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, wheelFortuneService, printerService):
        super(WheelSettingsWindow, self).__init__(parent)
        self.ui = Ui_WheelSettings()
        self.ui.setupUi(self)
        self.service = wheelFortuneService
        self.printerService = printerService

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.ticketCounterBox.setValue(printerService.getTicketCounter())

        self.ui.fortuneCheckBox.setChecked(self.service.isEnabled())
        self.ui.moneySpinBox.setText(str(self.service.moneyLevel()))

        self.wheelFortuneService = wheelFortuneService
        self.wheelFortuneService.probabilitiesUpdated.connect(self.updateTable)
        self.wheelFortuneService.probabilitiesUpdated.connect(self.updateLabels)
        self.updateTable()
        self.updateLabels()

        self.ui.descriptionTicket.clicked.connect(lambda: self.printerService.printDescTicket(
            AppSettings.actualDeviceName(),
            self.wheelFortuneService.getAllCounts(),
            self.wheelFortuneService.getAllNames(),
            self.wheelFortuneService.getInitialProbabilityCounts(),
        ))

    def onOkButton(self):
        self.service.setSettings(self.ui.fortuneCheckBox.isChecked(), self.ui.moneySpinBox.value())
        self.printerService.setNewTicketCounter(self.ui.ticketCounterBox.value())
        self.accept()

    def updateTable(self):
        self.ui.probTableWidget.setRowCount(10)
        for prob, count, initCount, name, cost, index in zip(self.wheelFortuneService.getAllProbs(),
                                                  self.wheelFortuneService.getAllCounts(),
                                                  self.wheelFortuneService.getInitialProbabilityCounts(),
                                                  self.wheelFortuneService.getAllNames(),
                                                  self.wheelFortuneService.getAllCosts(),
                                                  range(0,10)):
            self.ui.probTableWidget.setItem(index, 0, QtWidgets.QTableWidgetItem(str(index)))
            self.ui.probTableWidget.setItem(index, 1, QtWidgets.QTableWidgetItem(str(cost)))
            self.ui.probTableWidget.setItem(index, 2, QtWidgets.QTableWidgetItem(str(initCount) + "/" + str(count)))
            self.ui.probTableWidget.setItem(index, 3, QtWidgets.QTableWidgetItem("{0:.2f}".format(prob)))
            self.ui.probTableWidget.setItem(index, 4, QtWidgets.QTableWidgetItem(str(name)))

    def updateLabels(self):
        data = self.wheelFortuneService.getTotalInfo()
        self.ui.totalCostLabel.setText(str(data[0]))
        self.ui.expectedEarningLabel.setText(str(data[1]))
        self.ui.leftCost.setText(str(self.wheelFortuneService.getLeftCost()))
