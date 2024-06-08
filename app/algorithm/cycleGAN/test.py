import os
import torchvision.transforms as transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader
from PIL import Image
import torch
from app.algorithm.cycleGAN.gb import Generator
from app.algorithm.cycleGAN.datasets import ImageDataset, ImageDataset2

class GeneratorImage():
    def __init__(self, list_A, list_B, checkpoint_dir, output_dir, width = 960, height = 512):
        batche_size = 1

        self.pathA = ''
        self.pathB = ''
        self.outputFiles = []

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        device = self.device
        self.netG_A2B = Generator().to(device)
        self.netG_B2A = Generator().to(device)

        self.netG_A2B.load_state_dict(torch.load(checkpoint_dir + '/netG_A2B.pth'))
        self.netG_B2A.load_state_dict(torch.load(checkpoint_dir + '/netG_B2A.pth'))

        self.netG_A2B.eval()
        self.netG_B2A.eval()

        transforms_ = [
            transforms.Resize([height, width], Image.BICUBIC), # type: ignore
            transforms.RandomCrop([height, width]),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]

        self.dataloader = DataLoader(
            ImageDataset2(list_A, list_B, transforms_),
            batch_size=batche_size,
            shuffle=False,
            num_workers=0,
        )
        self.createOutputDir(output_dir)
    def createOutputDir(self, output_dir):
        output_dir = output_dir.replace('\\', '/')
        dir = output_dir.split('/')[-1].split('.')[-1]
        content_name = dir.split('2')[0]
        style_name = dir.split('2')[1]
        pathA = os.path.join(output_dir, content_name)
        pathB = os.path.join(output_dir, style_name)

        if not os.path.exists(pathA):
            os.makedirs(pathA)
        if not os.path.exists(pathB):
            os.makedirs(pathB)
        
        self.pathA = pathA
        self.pathB = pathB

    def run(self):
        device = self.device
        for i, batch in enumerate(self.dataloader):
            real_A = torch.tensor(batch['A'], dtype=torch.float).to(device)
            real_B = torch.tensor(batch['B'], dtype=torch.float).to(device)

            fake_B = 0.5 * self.netG_A2B(real_A).data + 1.0
            fake_A = 0.5 * self.netG_B2A(real_B).data + 1.0

            pathA = str(batch['pathA'][0])
            pathA = pathA.split('/')[-1]
            pathA = os.path.join(self.pathA, pathA)

            pathB = str(batch['pathB'][0])
            pathB = pathB.split('/')[-1]
            pathB = os.path.join(self.pathB, pathB)

            save_image(fake_A, pathA, normalize=True)
            save_image(fake_B, pathB, normalize=True)

            self.outputFiles.append(pathA)
            self.outputFiles.append(pathB)
        return self.outputFiles
  
if __name__ == '__main__':
    list_A = ['']
    list_B = ['']
    checkpoint_dir = ''
    output_dir = ''
    generator = GeneratorImage(list_A, list_B, checkpoint_dir, output_dir)
    generator.run()