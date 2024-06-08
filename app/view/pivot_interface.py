from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from qfluentwidgets import Pivot, qrouter
from app.common.style_sheet import StyleSheet
from app.view.cycle_g_a_n_interface import CycleGANInterface
from app.view.train_interface import TrainInterface
from app.view.vgg_interface import VGGInterface
from PySide6.QtCore import Qt
# tab 切换页
class PivotInterface(QWidget):
    """ Pivot interface """
    Nav = Pivot
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vggInterface = VGGInterface(self)
        self.trainInterface = TrainInterface(self)
        self.cycleGANInterface = CycleGANInterface(self)

        # add items to pivot
        self.addSubInterface(self.vggInterface, 'vggInterface', self.tr('VGG'))
        self.addSubInterface(self.trainInterface, 'trainInterface', self.tr('train'))
        self.addSubInterface(self.cycleGANInterface, 'cycleGANInterface', self.tr('cycle'))

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.vggInterface)
        self.pivot.setCurrentItem(self.vggInterface.objectName())

        qrouter.setDefaultRouteKey(self.stackedWidget, self.vggInterface.objectName())

    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())
