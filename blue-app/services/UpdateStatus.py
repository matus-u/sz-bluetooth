from PyQt5 import QtCore

from services import TimerService
from services.AppSettings import AppSettings
from services.LoggingService import LoggingService

import requests
import sys
import json

class UpdateStatus(TimerService.TimerStatusObject):

    def __init__(self, macAddr):
        super().__init__(3000)
        self.macAddr = macAddr
        self.start()

    def onTimeout(self):
        logger = LoggingService.getLogger()
        logger.info("Update state to server with id: %s" % self.macAddr)
        try:
            data = json.dumps({ 'dev' : {}})
            URL = "http://172.17.0.1:4000/api/devices/" + self.macAddr
            response = requests.put(URL, headers = {'Content-type': 'application/json'}, data = data, timeout = 2)
            response.raise_for_status()
            json_data = json.loads(response.text)
            AppSettings.storeServerSettings(json_data["data"]["name"], json_data["data"]["owner"], json_data["data"]["desc"], json_data["data"]["service_phone"])
            logger.info("Update state finished correctly!")
        except:
            logger.info("Update state finished with error %s" % str(sys.exc_info()[0]))
