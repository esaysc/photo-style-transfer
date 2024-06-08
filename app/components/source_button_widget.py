import itertools
import os
import shutil
from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QGridLayout, QVBoxLayout
from qfluentwidgets import ImageLabel, Flyout, FlyoutAnimationType, InfoBarIcon, MessageBox
from PySide6.QtGui import QImageReader, QPixmap
from .custom_message_box import CustomMessageBox
from app.common.config import cfg

class SourceButtonWidget(QWidget):
    """ Source button widget """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.dialog = QFileDialog()
        self.dialogFiles = QFileDialog()
        self.paths = []
        self.path = ''
        self.imageLabel = ImageLabel()
        self.w = 0
        self.h = 0
        self.parentWidth = 600
        self.dir_name = ''
        self.modePath = ''

        self.setup_dialog()  # 在展示对话框前先完成设置
        self.setup_dialog_files()
        self.setObjectName('sourceButtonWidget')

        self.sourceButton = QPushButton()
        self.sourceButton.setObjectName('sourceButton')

        self.selectsButton = QPushButton(self)
        self.selectsButton.setObjectName('selectsButton')

        self.trainButton = QPushButton(self)
        self.trainButton.setObjectName('trainButton')
        
        # 连接信号与槽
        self.sourceButton.clicked.connect(self.dialog.open)
        self.selectsButton.clicked.connect(self.dialogFiles.open)


    def loadImage(self, path):
        """加载图片"""
        self.path = path
        QImageReader.setAllocationLimit(0)     # 解决图片过大导致内存溢出 禁用限制 (更改这个 128 兆字节的限制)
        img = QPixmap(path)   # 加入圖片
        # print("file name => ", self.dialog.selectedFiles()[0].split("/")[-1])
        self.imageLabel.setImage(img)
        self.w = img.width()
        self.h = img.height()
        self.imageLabel.scaledToWidth(int(img.width()*(1)/4))
    def showSimpleFlyout(self, title, content, target):
        Flyout.create(
            icon=InfoBarIcon.INFORMATION,
            title=title,
            content=content,
            target=target,
            parent=self.window()
        )
    def loadImagesToColumn(self, paths, grid: QGridLayout, row, col, isCopy=True):
        """加载图片"""
        QImageReader.setAllocationLimit(0)     # 解决图片过大导致内存溢出 禁用限制 (更改这个 128 兆字节的限制)
        qVB = QVBoxLayout()
        for path in paths:
            img = QPixmap(path)   # 加入圖片
            imageLabel = ImageLabel()
            imageLabel.setImage(img)
            w = img.width()
            h = img.height()
            if w > h:
                imageLabel.scaledToWidth(int(960*0.25))
            else:
                imageLabel.scaledToHeight(int(960*0.25))
            qVB.addWidget(imageLabel)
        grid.addLayout(qVB, row, col, 1, 1)

        if isCopy:
            w = CustomMessageBox("复制到项目路径", "请输入文件夹名", self.window())
            if w.exec():
                print(w.urlLineEdit.text())
                self.dir_name = w.urlLineEdit.text()
            else:
                self.showSimpleFlyout(self.tr("提示"), self.tr("已取消选择"), self.selectsButton)
                return
            self.paths = paths
            self.copyLocalImage(dir=self.dir_name)
        else:
            self.paths = list(itertools.chain(self.paths, paths))
            

    def copyLocalImage(self, dir='', paths=[]):
        if dir == '':
            dir = self.dir_name
        if paths == []:
            paths = self.paths

        if len(paths) == 0:
            print("复制图片 缺少参数")
        else:
            self.modePath = os.path.join(cfg.models.value, dir)
            modePath = self.modePath
            datasets = cfg.datasets.value
            dst_dir = os.path.join(datasets, dir)
            if os.path.isdir(dst_dir) and self.showMessageDialog(self.tr("检查文件路径"), self.tr("文件夹已存在，是否需要销毁原文件夹中的文件")):
                shutil.rmtree(modePath)
            for path in paths:
                print("原文件路径 => ", path)
                filename = path.split("/")[-1]
                dst_file = os.path.join(dst_dir, filename)
                print("导入项目后文件路径 => ", dst_file)
                self.copy_file(path, dst_file)
            print("复制图片完成")

    def showMessageDialog(self, title, content):
        w = MessageBox(title, content, self.window())
        w.setContentCopyable(True)
        return w.exec()
    
    def copy_file(self, src_file, dst_file):
        dir = os.path.dirname(dst_file)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        if src_file.split('/')[-1] == dst_file.split('/')[-1]:
            if ~(self.showMessageDialog(self.tr("复制图片"), self.tr("文件已存在，是否覆盖"))):
                self.showSimpleFlyout(self.tr("提示"), self.tr("文件已存在，放弃操作"), self.selectsButton)
        shutil.copy(src_file, dst_file)
    def copy_files(self, src_dir, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file in os.listdir(src_dir):
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            if os.path.isfile(src_file):
                shutil.copy(src_file, dst_dir)
            if os.path.isdir(src_file):
                self.copy_files(src_file, dst_file)

    def loadImages(self, paths, grid: QGridLayout):
        """加载图片"""
        self.paths = paths
        totalW = self.parentWidth
        count = 1
        QImageReader.setAllocationLimit(0)     # 解决图片过大导致内存溢出 禁用限制 (更改这个 128 兆字节的限制)
        for path in paths:
            img = QPixmap(path)   # 加入圖片
            imageLabel = ImageLabel()
            imageLabel.setImage(img)
            w = img.width()
            h = img.height()
            if w > h:
                imageLabel.scaledToWidth(int(960*0.25))
            else:
                imageLabel.scaledToHeight(int(960*0.25))
            totalW += int(imageLabel.width())
            if totalW < self.parentWidth:
                grid.addWidget(imageLabel, grid.rowCount()-1, count, 1, 1)
            else:
                count = 0
                totalW = 0
                grid.addWidget(imageLabel, grid.rowCount(), count, 1, 1)
            print("totalw => {}, count => {}".format(totalW, count))
            count+=1

    def setup_dialog(self) -> None:
        """设置文件对话框"""
        # 接受模式
        self.dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)  # 文件将用于打开
        # 文件模式
        self.dialog.setFileMode(QFileDialog.FileMode.ExistingFile)  # 只能选择单个现有文件
        self.dialog.setNameFilter('图片文件(*.jpg *.png *.jpeg)')
        # self.dialog.setNameFilter('图片文件(*.jpg *.png *.bmp *.ico *.gif)')
    def setup_dialog_files(self) -> None:
        """设置文件对话框"""
        # 接受模式
        self.dialogFiles.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)  # 文件将用于打开
        # 文件模式
        self.dialogFiles.setFileMode(QFileDialog.FileMode.ExistingFiles)  # 只能选择单个现有文件
        self.dialogFiles.setNameFilter('图片文件(*.jpg *.png *.jpeg)')
    def showFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.INFORMATION,
            title='Lesson 4',
            content="取消选择",
            target=self.sourceButton,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
