# coding:utf-8
import os
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QIODevice, QIODeviceBase

from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.view.main_window import MainWindow
from app.page.add_page import AddPage

def loadUi(ui_file_name):
        ui_file_name = os.path.join(os.path.dirname(__file__)+"\\app\\ui\\", ui_file_name)
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODeviceBase.OpenModeFlag.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        ui = loader.load(ui_file)
        ui_file.close()
        if not ui:
            print(loader.errorString())
            sys.exit(-1)
        return ui

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
loader = QUiLoader()

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
w = MainWindow()
a = AddPage(w)

w.show()

app.exec()