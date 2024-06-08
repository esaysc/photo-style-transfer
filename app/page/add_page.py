import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QDesktopServices, QColor
from qfluentwidgets import NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow
from PySide6.QtCore import QFile, QIODevice

from ..view.main_window import MainWindow
from .transfer_interface import TransferInterface
from ..common.translator import Translator
from ..common.icon import Icon

# 对于引用 ui 文件的页面 进行 统一初始化
class AddPage:
    def __init__(self, w: MainWindow):
        super().__init__()
        self.pageDict = {}
        self.w = w
        t = Translator()
        pos = NavigationItemPosition.SCROLL
        self.w.transferInterface = TransferInterface(self.w)
        self.w.addSubInterface(self.w.transferInterface, Icon.TRANSFER, t.transfer, pos)
    
        