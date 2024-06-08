import glob
import random
from torch.utils.data import Dataset
from PIL import Image
import os, sys
import torchvision.transforms as transforms
from torchvision.transforms.functional import InterpolationMode
class ImageDataset(Dataset):
  def __init__(self, pathA, pathB, transforms_=None, mode='train'):
    self.transform = transforms.Compose(transforms_)
    current_path = os.path.abspath(sys.argv[0])

    self.pathA = pathA
    self.pathB = pathB

    self.list_A = glob.glob(self.pathA+ "/*")
    self.list_B = glob.glob(self.pathB+"/*")

    print(len(self.list_A), len(self.list_B))
  def __getitem__(self, index):
    pathA = self.list_A[index % len(self.list_A)]
    pathB = random.choice(self.list_B)
    print("pathA => ", pathA)
    print("pathB => ", pathB)
    img_A = Image.open(pathA).convert('RGB')
    img_B = Image.open(pathB).convert('RGB')
    print(" img_A.size => ", img_A.size)
    print("img_B.size => ", img_B.size)
    item_A = self.transform(img_A)
    item_B = self.transform(img_B)
    return {'A': item_A, 'B': item_B, 'pathA': pathA, 'pathB': pathB}

  def __len__(self):
    return max(len(self.list_A), len(self.list_B))


class ImageDataset2(Dataset):
  
  def __init__(self, list_A, list_B, transforms_=None, mode='test'):
    self.transform = transforms.Compose(transforms_)
    self.list_A = list_A
    self.list_B = list_B

    print(len(self.list_A), len(self.list_B))
  def __getitem__(self, index):
    pathA = self.list_A[index % len(self.list_A)]
    pathB = self.list_B[index % len(self.list_B)]
    
    # pathB = random.choice(self.list_B)
    # print("pathA => ", pathA)
    # print("pathB => ", pathB)
    img_A = Image.open(pathA).convert('RGB')
    img_B = Image.open(pathB).convert('RGB')
    # print(" img_A.size => ", img_A.size)
    # print("img_B.size => ", img_B.size)
    item_A = self.transform(img_A)
    item_B = self.transform(img_B)
    return {'A': item_A, 'B': item_B, 'pathA': pathA.replace("\\", "/"), 'pathB': pathB.replace("\\", "/")}

  def __len__(self):
    return max(len(self.list_A), len(self.list_B))


  
if __name__ == '__main__':
  from torch.utils.data import DataLoader
  pathA = ''
  pathB = ''
  # transforms_ = [
  #   transforms.Resize((256, 256)),
  #   transforms.ToTensor(),
  #   transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
  # ]
  transforms_ = [transforms.Resize(256, InterpolationMode.BILINEAR), transforms.ToTensor()]
  dataset = ImageDataset(pathA, pathB, transforms_=transforms_, mode="train")
  dataloader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=1)
  
def printData(dataloader):
    for i, batch in enumerate(dataloader):
      print(i)
      print(batch)
  
