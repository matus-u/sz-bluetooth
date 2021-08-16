from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys, os

from ui import ApplicationWindow
from ui import FocusHandler

from services.AppSettings import AppSettings
from services.TimerService import TimerService
from services.UpdateStatus import WebSocketStatus
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker
from services.AdminModeTracker import AdminModeTracker
from services.WheelFortuneService import WheelFortuneService
from services.LedButtonService import LedButtonService
from services.HwErrorHandling import HwErrorHandling
from services.PixmapService import PixmapService
from services.TestModeService import TestModeService
from services.LangBasedSettings import LangBasedSettings

from generated import Resources

if os.getenv('RUN_FROM_DOCKER', False) == False:
    from services.GpioService import GpioService
    from services.PrinterService import PrintingService
    from services.VolumeService import VolumeService
else:
    from services.mocks.GpioService import GpioService
    from services.mocks.PrinterService import PrintingService
    from services.mocks.VolumeService import VolumeService

def setStyle(app):
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("motif"))
    stylePath = ":/magento.qss" if LangBasedSettings.existMagentoTheme() else ":/dark-orange.qss" 
    styleFile = QtCore.QFile(stylePath)
    styleFile.open(QtCore.QIODevice.ReadOnly)
    data = styleFile.readAll()
    app.setStyleSheet(str(data, encoding="utf-8"))

def connectAdminModeTracker(adminModeTracker, applicationWindow, webUpdateStatus):

    adminModeTracker.adminModeInfoState.connect(webUpdateStatus.onAdminModeLocalChange, QtCore.Qt.QueuedConnection)
    webUpdateStatus.adminModeStateRequested.connect(adminModeTracker.informAboutActualState, QtCore.Qt.QueuedConnection)
    webUpdateStatus.adminModeServerRequest.connect(adminModeTracker.triggerAdminModeChange, QtCore.Qt.QueuedConnection)

    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+a"), applicationWindow, adminModeTracker.triggerAdminModeChange)
    adminModeTracker.adminModeInfoState.connect(applicationWindow.onAdminMode)
    adminModeTracker.adminModeLeaveTime.connect(applicationWindow.onAdminRemaining)
    applicationWindow.adminModeLeaveButton.connect(adminModeTracker.disableAdminMode)

def withdrawHappened(printingService, gain, prizes, moneyTotal, moneyFromLastWithdraw):
    printingService.printWithdrawTicket(AppSettings.actualDeviceName(), gain, prizes, AppSettings().actualInkeeperPercentile(), AppSettings().actualCurrency(), AppSettings.actualOwner(), AppSettings.actualAppVersion(), moneyTotal, moneyFromLastWithdraw)

def main():
    os.environ["QML2_IMPORT_PATH"]="resources/kbstyle"
    os.environ["QT_IM_MODULE"]="qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_LAYOUT_PATH"]="resources/kbstyle/layouts"
    os.environ["QT_VIRTUALKEYBOARD_STYLE"]="blue_app_kb"
    #os.environ["QT_LOGGING_RULES"]="qt.virtualkeyboard=true"

    LoggingService.init()
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":/arial-black.ttf")

    setStyle(app)
    AppSettings.restoreLanguage()
    AppSettings.restoreTimeZone()
    AppSettings.applySystemSoundVolumeLevel()

    errorHandler = HwErrorHandling()

    testModeService = TestModeService()

    volumeTimerService = TimerService()
    volumeService = VolumeService()
    volumeService.setVolume(AppSettings.actualVolumeAtStart())
    volumeTimerService.addTimerWorker(volumeService)

    testModeService.testModeEnabled.connect(volumeService.testModeEnabled, QtCore.Qt.QueuedConnection)
    testModeService.testModeDisabled.connect(volumeService.testModeDisabled, QtCore.Qt.QueuedConnection)

    updateStatusTimerService = TimerService()
    moneyTracker = MoneyTracker()

    gpioTimerService = TimerService()
    gpioService = GpioService()
    gpioTimerService.addTimerWorker(gpioService)

    adminModeTracker = AdminModeTracker(gpioService)

    wheelFortuneService = WheelFortuneService()
    printingService = PrintingService(errorHandler, wheelFortuneService)
    moneyTracker.withdrawHappened.connect(lambda gain, prizes, moneyTotal, moneyFromLastWithdraw: withdrawHappened(printingService, gain, prizes, moneyTotal, moneyFromLastWithdraw))

    pixmapService = PixmapService()

    webUpdateStatus = WebSocketStatus(sys.argv[1],
                                      moneyTracker,
                                      wheelFortuneService,
                                      printingService,
                                      errorHandler)

    updateStatusTimerService.addTimerWorker(webUpdateStatus)

    webUpdateStatus.newWinImage.connect(pixmapService.onNewImageData, QtCore.Qt.QueuedConnection)
    webUpdateStatus.newWinProbabilityValues.connect(wheelFortuneService.setNewProbabilityValues, QtCore.Qt.QueuedConnection)
    wheelFortuneService.probabilitiesUpdated.connect(webUpdateStatus.sendWinProbsStatus, QtCore.Qt.QueuedConnection)
    wheelFortuneService.reducePrizeCount.connect(webUpdateStatus.sendReducePrizeCount, QtCore.Qt.QueuedConnection)

    printingService.printStatusUpdated.connect(webUpdateStatus.sendPrintStatus, QtCore.Qt.QueuedConnection)
    printingService.ticketCounterChanged.connect(webUpdateStatus.sendPrintStatus, QtCore.Qt.QueuedConnection)
    printingService.printError.connect(lambda: wheelFortuneService.lockWheel())
    printingService.noPaper.connect(lambda: wheelFortuneService.lockWheel())
    printingService.enoughPaper.connect(lambda: wheelFortuneService.unlockWheel())

    timerService = TimerService()
    ledButtonService = LedButtonService(gpioService)
    timerService.addTimerWorker(ledButtonService)

    arrowHandler = FocusHandler.ArrowHandler(gpioService)


    AppSettings.getNotifier().moneyServerChanged.connect(lambda serverAddr: QtCore.QProcess.execute("scripts/update-money-server-logger.sh", [serverAddr]))

    LoggingService.getLogger().info("APPLICATION STARTED!0")
    application = ApplicationWindow.ApplicationWindow(timerService,
                                                      moneyTracker,
                                                      ledButtonService,
                                                      wheelFortuneService,
                                                      printingService,
                                                      arrowHandler,
                                                      errorHandler,
                                                      testModeService,
                                                      volumeService)

    #app.setOverrideCursor(QtCore.Qt.BlankCursor)


    connectAdminModeTracker(adminModeTracker, application, webUpdateStatus)
    webUpdateStatus.actualStateChanged.connect(application.onActualServerStateChanged, QtCore.Qt.QueuedConnection)

    LoggingService.getLogger().info("APPLICATION STARTED!1")
    application.show()
    LoggingService.getLogger().info("APPLICATION STARTED!2")
    printingService.initialize()
    LoggingService.getLogger().info("APPLICATION STARTED!3")
    volumeService.start()
    LoggingService.getLogger().info("APPLICATION STARTED!4")
    gpioService.start()
    LoggingService.getLogger().info("APPLICATION STARTED!5")

    application.onAdminMode(False)
    webUpdateStatus.asyncConnect()

    app.installEventFilter(adminModeTracker)

    LoggingService.getLogger().info("APPLICATION STARTED!")
    ret = app.exec_()

    volumeService.stop()
    gpioService.cleanup()
    application.cleanup()
    webUpdateStatus.asyncDisconnect()
    updateStatusTimerService.quit()
    volumeTimerService.quit()
    timerService.quit()
    sys.exit(ret)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LoggingService.getLogger().error("GENERAL EXCEPTION %s:" % str(e))
        raise e
