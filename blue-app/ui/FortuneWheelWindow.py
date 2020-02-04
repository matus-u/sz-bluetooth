from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.FortuneWheel import Ui_FortuneWheel
from services.AppSettings import AppSettings
from services.LedButtonService import LedButtonService

from ui import FocusHandler

class FortuneWheelWindow(QtWidgets.QDialog):
    def __init__(self, parent, winningIndex, prizes, printingService, ledButtonService, arrowHandler):
        super(FortuneWheelWindow, self).__init__(parent)
        self.ui = Ui_FortuneWheel()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.arrowHandler = arrowHandler

        self.ui.backButton.clicked.connect(self.accept)
        self.ui.backButton.setEnabled(False)

        self.winningIndex = winningIndex
        self.realWin = (prizes[winningIndex] > 0)
        self.printingService = printingService
        self.ledButtonService = ledButtonService
        self.focusHandler = None

        scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(scene)

        x1 = 0
        y1 = 0
        x2 = -96
        y2 = -300
        x3 =  96
        y3 = -300
        x4 = 0
        y4 = -300

        startTriangle = scene.addPolygon(QtGui.QPolygonF([QtCore.QPoint(x1,y1), QtCore.QPoint(x2,y2), QtCore.QPoint(x3,y3)]), QtGui.QPen(QtCore.Qt.black), QtGui.QBrush(QtCore.Qt.green))
        startTriangle.setTransformOriginPoint(0,0);
        self.triangles = []

        colors = [ QtCore.Qt.cyan, QtCore.Qt.magenta, QtCore.Qt.yellow ]
        angle = 36
        for i in range (0,10):
            startTriangle.setRotation(i*angle)
            points = [startTriangle.mapToScene(x1,y1), startTriangle.mapToScene(x2,y2), startTriangle.mapToScene(x3,y3)]

            grad = QtGui.QLinearGradient(QtCore.QPointF(0, 0), startTriangle.mapToScene(x4,y4));
            grad.setColorAt(0.3, QtCore.Qt.yellow);
            grad.setColorAt(0.8, colors[i%2]);
            grad.setColorAt(1.0, QtCore.Qt.red);

            if (prizes[i] > 0):
                brush = grad
            else:
                brush = QtGui.QBrush(QtCore.Qt.gray)

            self.triangles.append(scene.addPolygon(QtGui.QPolygonF(points), QtGui.QPen(QtCore.Qt.black), brush))

            font = QtGui.QFont()
            font.setPointSize(45)
            textItem = scene.addText(str(i), font)
            textItem.setTransformOriginPoint(0,0)
            textItem.setRotation(i*angle)
            point = startTriangle.mapToScene(-(textItem.boundingRect().width()/2),-280)
            textItem.moveBy(point.x(), point.y())

        scene.removeItem(startTriangle)

        for i in self.triangles:
            i.setTransformOriginPoint(0,0)

        self.arrow = scene.addPolygon(QtGui.QPolygonF([QtCore.QPoint(10, 0),
                                                       QtCore.QPoint(-10, 0),
                                                       QtCore.QPoint(-10, -180),
                                                       QtCore.QPoint(0, -200),
                                                       QtCore.QPoint(10, -180),
                                                       ]), QtGui.QPen(QtCore.Qt.black), QtGui.QBrush(QtCore.Qt.green))

        self.arrow.setTransformOriginPoint(0,0);

        self.animations = []
        self.animationIndex = 0
        self.generateAnimations()

        QtCore.QTimer.singleShot(1000, lambda: self.onAnimationFinished())
        scene.setFocus()

        self.ledButtonService.setButtonState(LedButtonService.LEFT, False)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, False)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, False)

    def onAnimationFinished(self):
        if (self.animationIndex < len(self.animations)):
            self.animations[self.animationIndex].start()
        self.animationIndex = self.animationIndex + 1

    def onRotationChange(self, x):
            self.arrow.setRotation(x)

    def generateAnimations(self):
        animation = QtCore.QVariantAnimation(self)
        animation.valueChanged.connect(self.onRotationChange)
        animation.setStartValue(0);
        animation.setEndValue(360);
        animation.setDuration(4000);
        animation.setLoopCount(1);
        animation.finished.connect(self.onAnimationFinished)
        self.animations.append(animation)

        animation2 = QtCore.QVariantAnimation(self)
        animation2.valueChanged.connect(self.onRotationChange)
        animation2.setStartValue(0);
        animation2.setEndValue(360);
        animation2.setDuration(6000);
        animation2.setLoopCount(1);
        animation2.finished.connect(self.onAnimationFinished)
        self.animations.append(animation2)

        indexOfLastElement = self.winningIndex
        if indexOfLastElement == 0:
            indexOfLastElement = 10
        lastDur = 800 * indexOfLastElement
        lastEndValue = indexOfLastElement*36

        animation3 = QtCore.QVariantAnimation(self)
        animation3.valueChanged.connect(self.onRotationChange)
        animation3.setStartValue(0);
        animation3.setEndValue(lastEndValue);
        animation3.setDuration(lastDur);
        animation3.setLoopCount(1);
        animation3.finished.connect(self.lastAnimationFinished)
        self.animations.append(animation3)


    def resetFocus(self):
        if self.focusHandler:
            self.focusHandler.setFocus()

    def lastAnimationFinished(self):
        self.ui.backButton.setEnabled(True)
        if (self.realWin):
            self.ui.wheelLabel.setText(self.tr("Congratulation. Take your ticket! Number: {}").format(self.winningIndex))
            self.printingService.printTicket(AppSettings.actualDeviceName(), "None", self.winningIndex)
        else:
            self.ui.wheelLabel.setText(self.tr("Sorry, no win"))

        self.ui.backButton.setEnabled(True)
        self.focusHandler = FocusHandler.InputHandler([FocusHandler.ButtonFocusProxy(self.ui.backButton, self.ledButtonService, False)])
        self.arrowHandler.confirmClicked.connect(lambda: self.focusHandler.onConfirm())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.focusHandler.onConfirm())

