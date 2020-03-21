from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import json
import random

class WheelFortuneService(QtCore.QObject):
    SettingsPath = "../blue-app-configs/wheel-fortune.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Enabled = "Enabled"
    MoneyLevel = "MoneyLevel"
    Probabilities = "Probabilities"

    reducePrizeCount = QtCore.pyqtSignal(int)
    win = QtCore.pyqtSignal(int, int, str)

    probabilitiesUpdated = QtCore.pyqtSignal()

    fortuneDataChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.printerActive = 1

        self.tossTimer = QtCore.QTimer()
        self.tossTimer.timeout.connect(self.onTossTimeout)

        self.counter = 0.0
        self.settings = QtCore.QSettings(WheelFortuneService.SettingsPath, WheelFortuneService.SettingsFormat)
        self.probabilityValues = json.loads(self.settings.value(WheelFortuneService.Probabilities, json.dumps(self.defaultProbs())))

        self.winTries = 0

    def onTossTimeout(self):
        self.counter = 0
        self.fortuneDataChanged.emit()

    def defaultProbs(self):
        return { 'expected_earnings': 0, 'total_costs': 0,
                'cost_1': 0, 'cost_2': 0, 'cost_3': 0,
                'cost_4': 0, 'cost_5': 0, 'cost_6': 0,
                'cost_7': 0, 'cost_8': 0, 'cost_9': 0,
                'count_1': 0, 'count_2': 0, 'count_3': 0,
                'count_4': 0, 'count_5': 0, 'count_6': 0,
                'count_7': 0, 'count_8': 0, 'count_9': 0,
                'id': None, 'name_1': '', 'name_2': '',
                'name_3': '', 'name_4': '', 'name_5': '',
                'name_6': '', 'name_7': '', 'name_8': '',
                'name_9': '', 'prob_1': 0, 'prob_2': 0,
                'prob_3': 0, 'prob_4': 0, 'prob_5': 0,
                'prob_6': 0, 'prob_7': 0, 'prob_8': 0, 'prob_9': 0}

    def setSettings(self, enabled, moneyLevel):
        if (self.isEnabled() != enabled) or (moneyLevel != self.moneyLevel()):
            self.counter = 0.0
            self.settings.setValue(WheelFortuneService.Enabled, enabled)
            self.settings.setValue(WheelFortuneService.MoneyLevel, moneyLevel)
            self.fortuneDataChanged.emit()

    def isEnabled(self):
        return self.settings.value(WheelFortuneService.Enabled, False, bool)

    def moneyLevel(self):
        return self.settings.value(WheelFortuneService.MoneyLevel, 0.0, float)

    def moneyInserted(self, money):
        if self.isEnabled():
            self.tossTimer.start(5000)
            mLevel = self.moneyLevel()
            self.counter = round (self.counter + round(money, 2), 2)

            while (self.counter >= mLevel):
                self.counter = self.counter - self.moneyLevel()
                self.winTries = self.winTries + 1
            self.fortuneDataChanged.emit()

    def overtakeWinTries(self):
        if self.winTries > 0:
            count = self.winTries
            self.winTries = 0
            for i in range(0, count):
                self.tryWin()
            self.fortuneDataChanged.emit()

    def setNewProbabilityValues(self, values):
        self.probabilityValues = values
        self.settings.setValue(WheelFortuneService.Probabilities, json.dumps(self.probabilityValues))
        self.probabilitiesUpdated.emit()

    def getAllProbs(self):
        probs = [float((self.probabilityValues["prob_" + str(x)])) for x in range(1,10)]
        probs =  [(float(100) - sum(probs))] + probs
        return probs

    def getAllNames(self):
        names = [(self.probabilityValues["name_" + str(x)]) for x in range(1,10)]
        names =  ["None"] + names
        return names

    def getAllCounts(self):
        counts = [(self.probabilityValues["count_" + str(x)]) for x in range(1,10)]
        counts =  [-1] + counts
        return counts

    def getAllCosts(self):
        costs = [(self.probabilityValues["cost_" + str(x)]) for x in range(1,10)]
        costs =  [-1] + costs
        return costs

    def getTotalInfo(self):
        return (self.probabilityValues["total_costs"], self.probabilityValues["expected_earnings"])

    def getLeftCost(self):
        a = sum ([(int(self.probabilityValues["count_" + str(x)]) * int(self.probabilityValues["cost_" + str(x)])) for x in range(1,10)])
        return a

    def tryWin(self):
        if self.printerActive == 1:
            probs = self.getAllProbs()
            probs =  [(float(x) / 100) for x in probs]
            values = [x for x in range (0,10)]
            win = random.choices(values, probs)
            counts = self.getAllCounts()
            names = self.getAllNames()
            if win[0] > 0:
                key = "count_" + str(win[0])
                if self.probabilityValues[key] > 0:
                    self.probabilityValues[key] = self.probabilityValues[key] - 1
                    self.settings.setValue(WheelFortuneService.Probabilities, json.dumps(self.probabilityValues))
                    self.reducePrizeCount.emit(win[0])

            self.win.emit(win[0], counts[win[0]], names[win[0]])

    def actualProbs(self):
        return self.probabilityValues

    def lockWheel(self):
        self.printerActive = 0

    def getActualFortuneTryLevels(self):
        return [self.moneyLevel() - self.counter, self.winTries]

    def resetActualFortuneTryLevels(self):
        self.counter = 0.0
        self.winTries = 0
        self.fortuneDataChanged.emit()

