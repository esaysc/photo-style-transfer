import os
import glob
from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QSizePolicy
from app.algorithm.cycleGAN.train import Trainer
from app.components.source_button_widget import SourceButtonWidget
from app.components.out_button_widget import OutButtonWidget
from app.common.config import cfg


class TrainInterface(QWidget):
    """ Train interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('trainInterface')
        # 创建网格布局对象
        grid = QGridLayout(self)

            
        self.grid = grid
        self.setLayout(grid)

        contentWidget = SourceButtonWidget(self)
        styleWidget = SourceButtonWidget(self)
        trainWidget = SourceButtonWidget(self)

        self.contentWidget = contentWidget
        self.styleWidget = styleWidget
        self.trainWidget = trainWidget

        self.contentButton = contentWidget.selectsButton
        self.contentButton.setText('选择内容图片')
        self.styleButton = styleWidget.selectsButton
        self.styleButton.setText('选择风格图片')

        self.trainButton = trainWidget.trainButton
        self.trainButton.setText('训练模型')

        self.contentWidget.dialogFiles.filesSelected.connect(lambda paths: self.contentWidget.loadImagesToColumn(paths, grid, 2,0))
        self.styleWidget.dialogFiles.filesSelected.connect(lambda paths: self.styleWidget.loadImagesToColumn(paths, grid, 2,2))
        self.trainButton.clicked.connect(lambda: self.train())
        # 空行间距
        spacer = QSpacerItem(30, 30, QSizePolicy.Maximum) # type: ignore
        grid.addItem(spacer, 0, 0, 1, 1)
        grid.addWidget(self.contentButton, 1, 0, 1, 1)
        grid.addWidget(self.trainButton, 1, 1, 1, 1)
        grid.addWidget(self.styleButton, 1, 2, 1, 1)

        grid.addItem(spacer, 0, 0, 1, -1)

        grid.setColumnStretch(2, 1)
    def train(self):
        print("训练模型")
        c = self.contentWidget.modePath
        s = self.styleWidget.modePath
        list_c = glob.glob(c + '/*')
        list_s = glob.glob(s + '/*')
        if list_c == [] or list_s == []:
            self.trainWidget.showSimpleFlyout(self.tr("提示"), self.tr("没有选择内容图片或风格图片"), self.trainButton)
            return
        dir = c.split('\\')[-1] + "2" + s.split('\\')[-1]
        checkpoint_path = os.path.join(cfg.datasets.value, dir, "checkpoint")
        print(" checkpoint_path => ", checkpoint_path)
        if not os.path.isdir(checkpoint_path):
           os.makedirs(checkpoint_path)
        t = Trainer(c, s, checkpoint_path)
        t.train()

