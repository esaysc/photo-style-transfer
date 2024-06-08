
from qfluentwidgets import MessageBox, SubtitleLabel, LineEdit
class CustomMessageBox(MessageBox):
    """ Custom message box """

    def __init__(self,title,placeholderText, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(title)
        self.urlLineEdit = LineEdit()

        self.urlLineEdit.setPlaceholderText(placeholderText)
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
