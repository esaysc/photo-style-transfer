import datetime
import os
import glob
import uuid
from PySide6.QtWidgets import (QWidget, QGridLayout, QSpacerItem, 
                               QSizePolicy, QHBoxLayout, QLabel)
from app.components.source_button_widget import SourceButtonWidget
from app.components.out_button_widget import OutButtonWidget
from app.common.config import cfg
from qfluentwidgets import ComboBox, ProgressRing, SpinBox



class VGGInterface(QWidget):
    """ VGG interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # ---------------------------------- 初始化 ----------------------------------
        outputfile = cfg.outputFolder.value + '/image/' + datetime.date.today().strftime('%Y-%m-%d') + '/' + str(uuid.uuid4()) + '.jpg'
        print("outputfile => ", outputfile)

        self.content_img_path, self.style_img_path, self.output_img_path = '', '', outputfile

        # 创建网格布局对象
        grid = QGridLayout()
        self.setLayout(grid)
        # 空行间距
        spacer = QSpacerItem(10, 10, QSizePolicy.Maximum) # type: ignore

        # 创建输入、输出、风格 对象
        inputWidget = SourceButtonWidget()
        styleWidget = SourceButtonWidget()
        outWidget = OutButtonWidget()

        self.inputWidget = inputWidget
        self.styleWidget = styleWidget
        self.outWidget = outWidget

        # 初始化 输入、输出、风格 图片显示容器
        self.inputImageLabel = inputWidget.imageLabel
        self.outImageLabel = outWidget.imageLabel
        self.styleImageLabel = styleWidget.imageLabel

        self.inputButton = inputWidget.sourceButton
        self.styleButton = styleWidget.sourceButton
        self.outButton = outWidget.sourceButton
        
        self.inputButton.setText('选择输入图片')
        self.outButton.setText('风格迁移')
        self.styleButton.setText('选择风格图片')
        
        # progress ring
        ring = ProgressRing(self)
        ring.setFixedSize(80, 80)
        ring.setTextVisible(True)

        comboBox1 = ComboBox()
        comboBox2 = ComboBox()
        comboBox3 = ComboBox()

        # 添加选项
        items = ['0.25X', '0.5X', '0.75X', '1X', '1.25X', '1.5X', ] 

        # 设置网格自适应列
        # grid.setColumnStretch(1, 1)
        # grid.setColumnStretch(2, 1)
        # grid.setColumnStretch(3, 1)

        # 加入到网格布局

        # 第一行 显示输出图片路径
        grid.addWidget(outWidget.info_le,0,1,1,1)       # 显示文件最终选择路径
        grid.addWidget(outWidget.info_label,0,0,1,1)    # 显示当前选择路径

        # 第二行 显示选择图片按钮
        grid.addWidget(inputWidget.sourceButton, 1, 0, 1, 1)    
        grid.addWidget(outWidget.sourceButton, 1, 1, 1, 1)
        grid.addWidget(styleWidget.sourceButton, 1, 2, 1, 1)

        # 第三行 显示 图片
        grid.addWidget(self.inputImageLabel, 2, 0, 1, 1)
        grid.addWidget(self.outImageLabel, 2, 1, 1, 1)
        grid.addWidget(self.styleImageLabel, 2, 2, 1, 1)

        # 第四行 缩放按钮
        comboBox1.addItems(items)
        comboBox2.addItems(items)
        comboBox3.addItems(items)

        # 连接信号与槽
        inputWidget.dialog.fileSelected.connect(lambda path: self.setContentImgPath(path))
        styleWidget.dialog.fileSelected.connect(lambda path: self.setStyleImgPath(path))
        outWidget.sourceButton.clicked.connect(lambda: self.transfer())

        # self.inputImageLabel.setAlignment(Qt.AlignCenter) # type: ignore
        # self.outImageLabel.setAlignment(Qt.AlignCenter) # type: ignore
        # self.styleImageLabel.setAlignment(Qt.AlignCenter) # type: ignore

        # 当前选项的索引改变信号
        comboBox1.currentIndexChanged.connect(lambda index: self.scrollImage(inputWidget, index))
        comboBox2.currentIndexChanged.connect(lambda index: self.scrollImage(outWidget, index))
        comboBox3.currentIndexChanged.connect(lambda index: self.scrollImage(styleWidget, index))


        grid.addWidget(comboBox1, 3, 0, 1, 1)
        grid.addWidget(comboBox2, 3, 1, 1, 1)
        grid.addWidget(comboBox3, 3, 2, 1, 1)

    def scrollImage(self, inputWidget, index):
        inputWidget.imageLabel.scaledToWidth(int(inputWidget.w*(index+1)/4))
        # imageLabel.scaledToHeight(int(imageLabel.height()*index/4))

    def setContentImgPath(self, path):
        self.content_img_path = path
        self.inputWidget.loadImage(path)

    def setStyleImgPath(self, path):
        self.style_img_path = path
        self.styleWidget.loadImage(path)

    def setOutputImgPath(self, path):
        self.output_img_path = path

    def transfer(self):
        # self.output_img_path = self.outWidget.dialog.getExistingDirectory()
        # self.output_img_path = self.outWidget.dialog.getSaveFileName(self, "保存图片", "", "图片文件(*.jpg *.png *.jpeg)")[0]
        inputW = self.inputWidget.w
        inputH = self.inputWidget.h
        styleW = self.styleWidget.w
        styleH = self.styleWidget.h
        outputW = self.outWidget.w
        outputH = self.outWidget.h
        list = [inputW, inputH, styleW, styleH]
        inputList = [inputW, inputH]
        styleList = [styleW, styleH]

        k = inputW / inputH - styleW / styleH
        if abs(k) > 1: 
            print("输入图片宽高比与风格图片宽高比不匹配")
            print(k ,inputW, inputH, styleW, styleH, outputW, outputH)
            return
        else:
            outputW = int(inputW * 0.55)
            outputH = int(inputW * 0.55)   
        
        self.outWidget.transfer(self.content_img_path, self.style_img_path, self.output_img_path, outputW, outputH)


class ProgressWidget(QWidget):

    def __init__(self, widget, parent=None):
        super().__init__(parent=parent)
        hBoxLayout = QHBoxLayout(self)

        self.spinBox = SpinBox(self)
        self.spinBox.valueChanged.connect(widget.setValue)
        self.spinBox.setRange(0, 100)

        hBoxLayout.addWidget(widget)
        hBoxLayout.addSpacing(50)
        hBoxLayout.addWidget(QLabel(self.tr('Progress')))
        hBoxLayout.addSpacing(5)
        hBoxLayout.addWidget(self.spinBox)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.spinBox.setValue(0)

