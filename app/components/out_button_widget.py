from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QLineEdit, QLabel
from PySide6.QtGui import QImageReader, QPixmap
from qfluentwidgets import ImageLabel
from app.algorithm.vgg.vgg_torch import NeuralStyleTransfer

class OutButtonWidget(QWidget):
    """ OutButton widget """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('styleWidget')
        self.w = 0
        self.h = 0
        self.imageLabel = ImageLabel()
        self.sourceButton = QPushButton(self)
        self.content_img_path, self.style_img_path, self.output_img_path, = '', '', ''
        self.dialog = QFileDialog(self)  # 文件对话框
        self.info_le = QLineEdit(self)  # 用于显示最终选择
        self.info_label = QLabel(self)  # 用于显示当前选择

        self.sourceButton.setText('风格迁移')
    def transfer(self, content_img_path, style_img_path, output_img_path, w, h):
        print("风格迁移 启动")
        if(content_img_path == '' or style_img_path == '') :
            print("风格迁移 缺少参数")
            return
        else:
            print(content_img_path, style_img_path, output_img_path)
            # self.dialog.open()
            neural_style_transfer = NeuralStyleTransfer(content_img_path, style_img_path, output_img_path, width=w, height=h)
            self.loadImage(neural_style_transfer.run())

    def loadImage(self, path):
        """加载图片"""
        self.path = path
        QImageReader.setAllocationLimit(0)     # 解决图片过大导致内存溢出 禁用限制 (更改这个 128 兆字节的限制)
        img = QPixmap(path)   # 加入圖片
        # print("file name => ", self.dialog.selectedFiles()[0].split("/")[-1])
        self.imageLabel.setImage(img)
        self.w = img.width()
        self.h = img.height()
        self.imageLabel.scaledToWidth(int(img.width()*(3)/4))
