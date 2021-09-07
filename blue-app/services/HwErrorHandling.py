from PyQt5 import QtCore

from services.LoggingService import LoggingService

class HwErrorHandling(QtCore.QObject):

    COIN_MACHINE_CORRUPTED = 0
    PRINTER_CORRUPTED = 1
    NO_PAPER = 2

    hwErrorChanged = QtCore.pyqtSignal(object)

    def __init__(self, wheelFortuneService):
        super().__init__()
        self.errors = set()
        self.wheelFortuneService = wheelFortuneService

    def hwErrorClear(self, code):
        if code in self.errors:
            LoggingService.getLogger().error("CLEAR HW ERROR %s" % str(code))
            LoggingService.getLogger().error(self.getErrorDesc(code))
            LoggingService.getLogger().error("CLEAR HW ERROR - END %")
            self.errors.remove(code)
            self.hwErrorChanged.emit(self.getErrorDescs())

    def hwErrorEmit(self, code):
        if code not in self.errors:
            self.errors.add(code)
            LoggingService.getLogger().error("HW ERROR - %s" % str(code))
            LoggingService.getLogger().error(self.getErrorDesc(code))
            LoggingService.getLogger().error("HW ERROR - END")
            self.hwErrorChanged.emit(self.getErrorDescs())

    def getErrorDesc(self, code):
        if code == HwErrorHandling.COIN_MACHINE_CORRUPTED:
            return self.tr("Coin machine corrupted, call service please.")

        if code == HwErrorHandling.PRINTER_CORRUPTED:
            return self.tr("Printer machine corrupted, call service please.")

        if code == HwErrorHandling.NO_PAPER:
            return self.tr("No paper. Printer machine cannot operate, please insert paper.")

    def getErrorDescs(self):
        vals = []
        for x in self.errors:
            if (x in [HwErrorHandling.PRINTER_CORRUPTED, HwErrorHandling.NO_PAPER]) and (not self.wheelFortuneService.isEnabled()):
                continue
            vals.append(self.getErrorDesc(x))
        return vals

    def isPrinterErrorSet(self):
        return (HwErrorHandling.PRINTER_CORRUPTED in self.errors) or (HwErrorHandling.NO_PAPER in self.errors)

    def getPrinterErrorDescs(self):
        vals = []
        if HwErrorHandling.PRINTER_CORRUPTED in self.errors:
            vals.append(self.getErrorDesc(HwErrorHandling.PRINTER_CORRUPTED))
        if HwErrorHandling.NO_PAPER in self.errors:
            vals.append(self.getErrorDesc(HwErrorHandling.NO_PAPER))
        return vals
