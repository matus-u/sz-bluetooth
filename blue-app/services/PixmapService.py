from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import PathSettings

import base64

class PixmapService(QtCore.QObject):

    pixMaps = []

    @staticmethod
    def reloadPixMaps():
        PixmapService.pixMaps = []
        for i in range (0,10):
            path = PathSettings.AppBasePath() + "../blue-app-configs/images/{}.jpg".format(str(i))
            pix = QtGui.QPixmap(path)
            PixmapService.pixMaps.append(pix)

    def __init__(self):
        super().__init__()
        PixmapService.reloadPixMaps()

    def onNewImageData(self, payload):
        with open(PathSettings.AppBasePath() + "../blue-app-configs/images/{}.jpg".format(payload["index"]), "wb") as fh:
            fh.write(base64.b64decode(payload["data"]))
        PixmapService.reloadPixMaps()

