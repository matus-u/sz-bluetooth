from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.FortuneWheel import Ui_FortuneWheel

from services.AppSettings import AppSettings

class FortuneWheelWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super(FortuneWheelWindow, self).__init__(parent)
        self.ui = Ui_FortuneWheel()
        self.ui.setupUi(self)

        scene = QtWidgets.QGraphicsScene()

        self.ui.graphicsView.setScene(scene)

        x1 = 0
        y1 = 0
        x2 = -96
        y2 = -300
        x3 =  96
        y3 = -300

        startTriangle = scene.addPolygon(QtGui.QPolygonF([QtCore.QPoint(x1,y1), QtCore.QPoint(x2,y2), QtCore.QPoint(x3,y3)]), QtGui.QPen(QtCore.Qt.black), QtGui.QBrush(QtCore.Qt.green))
        startTriangle.setTransformOriginPoint(0,0);
        self.triangles = []

        colors = [ QtCore.Qt.cyan, QtCore.Qt.magenta, QtCore.Qt.yellow ]
        angle = 36
        for i in range (0,10):
            startTriangle.setRotation(i*angle)
            brush = QtGui.QBrush(colors[i%3])

            if i == 0:
                brush = QtGui.QBrush(QtCore.Qt.gray)
            self.triangles.append(scene.addPolygon(QtGui.QPolygonF([startTriangle.mapToScene(x1,y1), startTriangle.mapToScene(x2,y2), startTriangle.mapToScene(x3,y3)]), QtGui.QPen(QtCore.Qt.black), brush))

    #        font = QtGui.QFont()
    #        font.setPointSize(45)
    #        textItem = scene.addText(str(i), font)
    #        textItem.setTransformOriginPoint(0,0)
    #        textItem.setRotation(i*angle)
    #        point = startTriangle.mapToScene(-(textItem.boundingRect().width()/2),-280)
    #        textItem.moveBy(point.x(), point.y())

        scene.removeItem(startTriangle)

        for i in self.triangles:
            i.setTransformOriginPoint(0,0)

        self.animations = []
        self.animationIndex = 0
        self.generateAnimations(9)
        QtCore.QTimer.singleShot(1000, lambda: self.onAnimationFinished())

    def onAnimationFinished(self):
        if (self.animationIndex < len(self.animations)):
            self.animations[self.animationIndex].start()
        self.animationIndex = self.animationIndex + 1

    def onRotationChange(self, x):
        for i in self.triangles:
            i.setRotation(x)

    def generateAnimations(self, indexOfLastElement):
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

        lastDur = 800 * indexOfLastElement
        lastEndValue = indexOfLastElement*36

        animation3 = QtCore.QVariantAnimation(self)
        animation3.valueChanged.connect(self.onRotationChange)
        animation3.setStartValue(0);
        animation3.setEndValue(lastEndValue);
        animation3.setDuration(lastDur);
        animation3.setLoopCount(1);
        animation3.finished.connect(self.onAnimationFinished)
        if (lastDur > 0):
            self.animations.append(animation3)

