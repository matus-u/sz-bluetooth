from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LoggingService import LoggingService
from services import PathSettings

import json
import random
import copy
import os

class WheelFortuneService(QtCore.QObject):
    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/wheel-fortune.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Enabled = "Enabled"
    Probabilities = "Probabilities"
    InitProbabilities = "InitProbabilities"

    reducePrizeCount = QtCore.pyqtSignal(int)
    win = QtCore.pyqtSignal(int, str, float)

    probabilitiesUpdated = QtCore.pyqtSignal()

    winCounterChanged= QtCore.pyqtSignal()
    fortuneDataChanged = QtCore.pyqtSignal()
    fortuneTryFirstIncreased = QtCore.pyqtSignal()

    enabledNotification = QtCore.pyqtSignal(bool)

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
        self.winCounterChanged.emit()

    def defaultProbs(self):
        return { 'money_level': 1.0, 'expected_earnings': 0, 'total_costs': 0,
                'cost_0': 1.0, 'cost_1': 0, 'cost_2': 0,
                'cost_3': 0, 'cost_4': 0, 'cost_5': 0,
                'cost_6': 0, 'cost_7': 0, 'cost_8': 0,
                'cost_9': 0,
                'count_0': 0, 'count_1': 0, 'count_2': 0,
                'count_3': 0, 'count_4': 0, 'count_5': 0,
                'count_6': 0, 'count_7': 0, 'count_8': 0,
                'count_9': 0,
                'id': None,
                'name_0':'None', 'name_1': '', 'name_2': '',
                'name_3': '', 'name_4': '', 'name_5': '',
                'name_6': '', 'name_7': '', 'name_8': '',
                'name_9': '',
                'prob_0': 0.0, 'prob_1': 0, 'prob_2': 0,
                'prob_3': 0, 'prob_4': 0, 'prob_5': 0,
                'prob_6': 0, 'prob_7': 0, 'prob_8': 0,
                'prob_9': 0}

    def setSettings(self, enabled):
        self.enabledNotification.emit(enabled)
        if self.isEnabled() != enabled:
            self.counter = 0.0
            self.settings.setValue(WheelFortuneService.Enabled, enabled)
            self.fortuneDataChanged.emit()

    def isEnabled(self):
        return self.settings.value(WheelFortuneService.Enabled, False, bool)

    def moneyLevel(self):
        return self.probabilityValues.get("money_level", 1.0)

    def moneyInserted(self, money):
        if self.isEnabled():
            if (self.computeTotalPrizeCount(self.probabilityValues)) > 0:
                self.tossTimer.start(30000)
                mLevel = self.moneyLevel()
                self.counter = round (self.counter + round(money, 2), 2)

                while (self.counter >= mLevel):
                    self.counter = self.counter - self.moneyLevel()
                    self.winTries = self.winTries + 1
                    if (self.winTries == 1):
                        self.fortuneTryFirstIncreased.emit()
                self.winCounterChanged.emit()

    def overtakeWinTries(self):
        if self.winTries > 0:
            LoggingService.getLogger().info("Overtake win tries")
            self.winTries = self.winTries-1
            self.tryWin()

    def setNewProbabilityValues(self, values):
        self.probabilityValues = values
        self.settings.setValue(WheelFortuneService.InitProbabilities, json.dumps(self.probabilityValues))
        self.settings.setValue(WheelFortuneService.Probabilities, json.dumps(self.probabilityValues))
        self.probabilitiesUpdated.emit()
        self.fortuneDataChanged.emit()

    def getInitialProbabilityCounts(self):
        return self.parseCountsFromValues(json.loads(self.settings.value(WheelFortuneService.InitProbabilities, json.dumps(self.probabilityValues))))

    def parseCountsFromValues(self, values):
        return [(values["count_" + str(x)]) for x in range(0,10)]

    def parseProbsFromValues(self, values):
        return [(float((values["prob_" + str(x)]))) for x in range(0,10)]

    def parseCostsFromValues(self, values):
        return [(values["cost_" + str(x)]) for x in range(0,10)]

    def getAllNames(self):
        return [(self.probabilityValues["name_" + str(x)]) for x in range(0,10)]

    def getAllProbs(self):
        return self.parseProbsFromValues(self.probabilityValues)

    def getAllCounts(self):
        return self.parseCountsFromValues(self.probabilityValues)

    def getAllCosts(self):
        return self.parseCostsFromValues(self.probabilityValues)

    def getTotalInfo(self):
        return (self.probabilityValues["total_costs"], self.probabilityValues["expected_earnings"])

    def getLeftCost(self):
        return sum([(int(self.probabilityValues["count_" + str(x)]) * int(self.probabilityValues["cost_" + str(x)])) for x in range(1,10)])

    def hasTries(self):
        return self.winTries > 0

    def tryWin(self):
        if self.printerActive == 1:
            if (self.computeTotalPrizeCount(self.probabilityValues)) > 0:
                win = self.tossNumber(self.probabilityValues)
                self.settings.setValue(WheelFortuneService.Probabilities, json.dumps(self.probabilityValues))
                self.reducePrizeCount.emit(win)
                LoggingService.getLogger().info("Toss number " + str(win) + " " + self.getAllNames()[win])
                self.win.emit(win, self.getAllNames()[win], self.getAllCosts()[win])
            else:
                self.win.emit(0, self.getAllNames()[0], 0.0)

    def actualProbs(self):
        return self.probabilityValues

    def lockWheel(self):
        LoggingService.getLogger().info("Lock wheel!!!")
        self.printerActive = 0

    def unlockWheel(self):
        LoggingService.getLogger().info("Unlock wheel!!!")
        self.printerActive = 1

    def getActualFortuneTryLevels(self):
        return [self.moneyLevel() - self.counter, self.winTries]

    def actualPrizesCount(self):
        return sum([(self.probabilityValues["count_" + str(x)]) for x in range(1,10)])

    def resetActualFortuneTryLevels(self):
        LoggingService.getLogger().info("Reset actual fortune levels")
        self.counter = 0.0
        self.winTries = 0
        self.fortuneDataChanged.emit()

    def resetFortuneToDefault(self):
        if os.path.exists(WheelFortuneService.SettingsPath):
          os.remove(WheelFortuneService.SettingsPath)

    def lowestPrizeIndex(self, probabilityValues):
        ind = -1
        actualMin = float('inf')
        for i in range(1,10):
            if probabilityValues["count_" + str(i)] > 0:
                if probabilityValues["cost_" + str(i)] <= actualMin:
                    ind = i
                    actualMin = probabilityValues["cost_" + str(i)]
        return ind


    def tossNumber(self, probabilityValues):
        values = [x for x in range (0,10)]
        increaseBack = False
        incDecIndex = -1
        #Last prize has to be taken out
        if (self.computeTotalPrizeCount(probabilityValues)) > 1:
            increaseBack = True
            incDecIndex = self.lowestPrizeIndex(probabilityValues)
            self.updatePrizeCount(incDecIndex, probabilityValues, -1)

        self.recomputeProbs(probabilityValues)
        probs = self.parseProbsFromValues(probabilityValues)
        win = random.choices(values, self.parseProbsFromValues(probabilityValues))
        self.updatePrizeCount(win[0], probabilityValues, -1)
        #Last prize is given back
        if increaseBack:
            self.updatePrizeCount(incDecIndex, probabilityValues, 1)
        self.recomputeProbs(probabilityValues)
        return win[0]

    def testWinn(self):
        myTestProbsValues = copy.deepcopy(self.probabilityValues)
        wheelTurns = self.computeTotalPrizeCount(myTestProbsValues)
        result = ""
        winGames = 0

        for i in range (0,wheelTurns):
            win = self.tossNumber(myTestProbsValues)
            if win > 0:
                result = result + "1"
                winGames = winGames+1
            else:
                result = result + "0"
        return "Count of games: " + str(wheelTurns) + "\n" + "Win games: " + str(winGames) + "\n" + result

    def updatePrizeCount(self, index, probabilityValues, change):
        probabilityValues["count_" + str(index)] = probabilityValues["count_" + str(index)] + change

    def computeTotalPrizeCount(self, probabilityValues):
        return sum([int(probabilityValues["count_" + str(x)]) for x in range(0,10)])

    def recomputeProbs(self, probabilityValues):
        totalPrizesCount = self.computeTotalPrizeCount(probabilityValues)
        for i in range(0,10):
            if (totalPrizesCount > 0):
                probabilityValues["prob_" + str(i)] = (float(probabilityValues["count_" + str(i)]) / float(totalPrizesCount))
            else:
                probabilityValues["prob_" + str(i)] = 0.0

    def isPossibleWin(self, probabilityValues):
        return self.computeTotalPrizeCount(probabilityValues) > 0
