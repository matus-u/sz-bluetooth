from PyQt5 import QtCore

from services import TimerService
from services.AppSettings import AppSettings
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker

import requests
import sys
import json

class UpdateStatus(TimerService.TimerStatusObject):

    def __init__(self, macAddr, moneyTracker):
        super().__init__(3000)
        self.macAddr = macAddr
        self.moneyTracker = moneyTracker
        self.start()

    def onTimeout(self):
        logger = LoggingService.getLogger()
        logger.info("Update state to server with id: %s" % self.macAddr)
        try:
            counters = self.moneyTracker.getCounters()
            data = json.dumps({ 'dev' : {
                "money_total" : counters[MoneyTracker.TOTAL_COUNTER_INDEX],
                "money_from_last_withdraw" : counters[MoneyTracker.FROM_LAST_WITHDRAW_COUNTER_INDEX]
            }})
            URL = "http://172.17.0.1:4000/api/devices/" + self.macAddr
            response = requests.put(URL, headers = {'Content-type': 'application/json'}, data = data, timeout = 2)
            response.raise_for_status()
            json_data = json.loads(response.text)
            AppSettings.storeServerSettings(json_data["data"]["name"], json_data["data"]["owner"], json_data["data"]["desc"], json_data["data"]["service_phone"])
            logger.info("Update state finished correctly!")
        except:
            logger.info("Update state finished with error %s" % str(sys.exc_info()[0]))
