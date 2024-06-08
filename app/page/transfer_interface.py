from app.view.pivot_interface import PivotInterface
from app.view.pivot_interface import PivotInterface
from ..common.translator import Translator
from ..view.gallery_interface import GalleryInterface
from ..common.translator import Translator
from ..view.gallery_interface import GalleryInterface

class TransferInterface(GalleryInterface):
    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.transfer,
            subtitle='图像艺术风格迁移',
            parent=parent
        )
        self.setObjectName('transferInterface')
        self.stretch = 0
        self.addExampleCard(
            "图像风格转化",
            widget=PivotInterface(self),
            sourcePath='www',
        )
