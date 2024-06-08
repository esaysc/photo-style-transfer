import datetime
import os
import glob
from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QSizePolicy, QVBoxLayout, QPushButton
from qfluentwidgets import ComboBox, ImageLabel
from app.algorithm.cycleGAN.test import GeneratorImage
from app.components.source_button_widget import SourceButtonWidget
from app.common.config import cfg
class CycleGANInterface(QWidget):
    """ cycleGAN interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('cycleGANInterface')

        # pth模型 选择
        self.pthBox = ComboBox(self)
        self.pths = []
        self.pth = ''
        self.__init()
        self.connectSignalToSlot()
       
        # 创建网格布局对象
        grid = QGridLayout()

        self.grid = grid
        self.setLayout(grid)
        contentWidget = SourceButtonWidget()
        styleWidget = SourceButtonWidget()

        self.contentWidget = contentWidget
        self.styleWidget = styleWidget

        self.contentButton = contentWidget.selectsButton
        self.contentButton.setText('选择内容图片')
        self.styleButton = styleWidget.selectsButton
        self.styleButton.setText('选择风格图片')

        self.createButton = QPushButton(self)
        self.createButton.setText('生成图片')

        self.contentWidget.dialogFiles.filesSelected.connect(lambda paths: self.contentWidget.loadImagesToColumn(paths, grid, 2,0, isCopy=False))
        self.styleWidget.dialogFiles.filesSelected.connect(lambda paths: self.styleWidget.loadImagesToColumn(paths, grid, 2,2, isCopy=False))
        
        self.createButton.clicked.connect(lambda: self.create())
        # 空行间距
        spacer = QSpacerItem(30, 30, QSizePolicy.Maximum) # type: ignore
        grid.addItem(spacer, 0, 0, 1, 1)
        grid.addWidget(self.contentButton, 1, 0, 1, 1)
        grid.addWidget(self.createButton, 1, 1, 1, 1)
        grid.addWidget(self.styleButton, 1, 2, 1, 1)

        # grid.addItem(spacer, 0, 0, 1, -1)

        grid.setColumnStretch(2, 1)

    def __init(self):
        self.init_pth_list()

    def init_pth_list(self):
        pthBox = self.pthBox
        pthBox.setCurrentIndex(0)
        pthBox.setMinimumWidth(210)
        print("cfg.models.value => ", cfg.models.value)
        dir = os.path.join(cfg.models.value)
        print("dir =>", dir)
        if os.path.isdir(dir):
            for root, dirs, files in os.walk(dir):
                print("dirs => ", dirs)
                pthBox.addItems(dirs)
                for dir in dirs:
                    self.pths.append(os.path.join(root, dir, "checkpoint"))
                self.updatePth(0)
                return
        else:
            pthBox.addItem("没有模型")

    def connectSignalToSlot(self):
        # 当前选项的索引改变信号
        self.pthBox.currentIndexChanged.connect(lambda index: self.updatePth(index))

    def updatePth(self, index):
        self.pthIndex = index
        self.pth = self.pths[index]
        print(index, self.pths)

    def create(self):
        print("尝试生成图片")
        list_A = self.contentWidget.paths
        list_B = self.styleWidget.paths
        pth = self.pth
        if len(list_A) == 0 or len(list_B) == 0 or self.pth == '':
            self.contentWidget.showSimpleFlyout(self.tr("提示"), self.tr("没有选择内容图片或风格图片或模型"), self.createButton)
        print("self.pth => ", self.pth)

        print("list_A => {}, list_B => {}".format(list_A, list_B))
        output_dir = os.path.join(cfg.outputFolder.value, "image", str(datetime.date.today().strftime('%Y-%m-%d')))
        # if not os.path.isdir(output_dir):
        #     os.makedirs(output_dir)
        output_dir = output_dir.replace('\\', '/')
        pth = self.pth.replace('\\', '/')
        output_dir = os.path.join(output_dir, pth.split('/')[-2])
        print("output_dir => ", output_dir)
        g = GeneratorImage(list_A, list_B, self.pth, output_dir)
        outputFiles = g.run()
        contentOut = QVBoxLayout()
        styleOut = QVBoxLayout()

        for i in range(len(outputFiles)):
            imag = ImageLabel(outputFiles[i])
            imag.scaledToWidth(int(960*0.25))
            if i%2 == 0:
                styleOut.addWidget(imag)
            else:
                contentOut.addWidget(imag)

        self.grid.addLayout(contentOut, 2, 1, 1, 1)
        self.grid.addLayout(styleOut, 2, 3, 1, 1)
