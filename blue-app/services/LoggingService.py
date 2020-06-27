import logging
from logging.handlers import RotatingFileHandler

from services import PathSettings

class LoggingService():
    logger = None

    @staticmethod
    def init():
        LoggingService.logger = logging.getLogger("RotatingLogger")
        LoggingService.logger.setLevel(logging.INFO)

        # add a rotating handler
        handler = RotatingFileHandler(PathSettings.AppBasePath() + "../blue-app-configs/logging/blue-app.log", maxBytes=2000000,
                                      backupCount=2)
        FORMAT = "[%(asctime)s - %(filename)s: %(funcName)s() ] %(message)s"
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        LoggingService.logger.addHandler(handler)

    @staticmethod
    def getLogger():
        return LoggingService.logger
