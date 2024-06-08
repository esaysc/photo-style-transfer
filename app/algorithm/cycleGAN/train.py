from tabnanny import check
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from PIL import Image
import torch
from app.algorithm.cycleGAN.gb import Discriminator, Generator 
from app.algorithm.cycleGAN.datasets import ImageDataset 
from app.algorithm.cycleGAN.utils import ReplayBuffer, LambdaLR, weights_init_normal
import itertools
import tensorboardX

class Trainer():
    def __init__(self, pathA, pathB, checkpoint_path, log_path=''):
        super().__init__()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.checkpoint_path = checkpoint_path

        batche_size = 1
        size = 256

        self.width = 960
        self.height =512
        
        lr = 0.0002
        self.n_epoch = 200
        epoch = 0
        decay_epoch = 100

        # networks
        self.netG_A2B = Generator().to(self.device)
        self.netG_B2A = Generator().to(self.device)
        self.netD_A = Discriminator().to(self.device)
        self.netD_B = Discriminator().to(self.device)

        # loss
        self.loss_GAN = torch.nn.MSELoss()
        self.loss_cycle = torch.nn.L1Loss()
        self.loss_identity = torch.nn.L1Loss()

        # optimizer & LR
        self.opt_G = torch.optim.Adam(
            itertools.chain(self.netG_A2B.parameters(), self.netG_B2A.parameters()), lr=lr, betas=(0.5, 0.9999)
        )

        self.opt_DA = torch.optim.Adam(self.netD_A.parameters(), lr=lr, betas=(0.5, 0.9999))
        self.opt_DB = torch.optim.Adam(self.netD_B.parameters(), lr=lr, betas=(0.5, 0.9999))

        self.lr_scheduler_G = torch.optim.lr_scheduler.LambdaLR(self.opt_G, lr_lambda=LambdaLR(self.n_epoch, epoch, decay_epoch).step)
        self.lr_scheduler_DA = torch.optim.lr_scheduler.LambdaLR(self.opt_DA, lr_lambda=LambdaLR(self.n_epoch, epoch, decay_epoch).step)
        self.lr_scheduler_DB = torch.optim.lr_scheduler.LambdaLR(self.opt_DB, lr_lambda=LambdaLR(self.n_epoch, epoch, decay_epoch).step)

        self.input_A = torch.ones([1, 3, size, size], dtype=torch.float).to(self.device)
        self.input_B = torch.ones([1, 3, size, size], dtype=torch.float).to(self.device)

        self.label_real = torch.ones([1], dtype=torch.float, requires_grad=False).to(self.device)
        self.label_fake = torch.zeros([1], dtype=torch.float, requires_grad=False).to(self.device)

        self.fake_A_buffer = ReplayBuffer()
        self.fake_B_buffer = ReplayBuffer()
        if log_path=='':
            log_path = r'M:\python\photo-style-transfer\app\output\logs'
        self.writer_log = tensorboardX.SummaryWriter(log_path)

        transforms_ = [
            transforms.Resize(int(size * 1.12), Image.BICUBIC), # type: ignore
            transforms.RandomCrop(size),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]

        self.dataloader = DataLoader(
            ImageDataset(pathA, pathB, transforms_=transforms_),
            batch_size=batche_size,
            shuffle=True,
            num_workers=0,
        )

    def train(self):
        step = 1
        # training loop
        for epoch in range(self.n_epoch):
            print('======================== Epoch: %d ========================' % epoch)
            for i, batch in enumerate(self.dataloader):

                print()
                print("i => ", i)
                print()

                real_A = torch.tensor(batch['A'], dtype=torch.float).to(self.device)
                real_B = torch.tensor(batch['B'], dtype=torch.float).to(self.device)
                # real_B = batch['B'].to(self.device)

                self.opt_G.zero_grad()

                same_B = self.netG_A2B(real_B)
                self.loss_identity_B = self.loss_identity(same_B, real_B) * 5.0
                same_A = self.netG_B2A(real_A)
                self.loss_identity_A = self.loss_identity(same_A, real_A) * 5.0

                # train discriminator A
                fake_B = self.netG_A2B(real_A)
                pred_fake = self.netD_B(fake_B)
                self.loss_GAN_A2B = self.loss_GAN(pred_fake, self.label_real)

                fake_A = self.netG_B2A(real_B)
                pred_fake = self.netD_A(fake_A)
                self.loss_GAN_B2A = self.loss_GAN(pred_fake, self.label_real)

                # cycle loss
                recovered_A = self.netG_B2A(fake_B)
                self.loss_cycle_ABA = self.loss_cycle(recovered_A, real_A) * 10.0

                recovered_B = self.netG_A2B(fake_A)
                self.loss_cycle_BAB = self.loss_cycle(recovered_B, real_B) * 10.0

                # total loss
                loss_G = self.loss_identity_A + self.loss_identity_B + self.loss_GAN_A2B + self.loss_GAN_B2A + self.loss_cycle_ABA + self.loss_cycle_BAB
                loss_G.backward()
                self.opt_G.step()

                # ===============================================
                self.opt_DA.zero_grad()

                pred_real = self.netD_A(real_A)
                loss_D_real = self.loss_GAN(pred_real, self.label_real)

                fake_A = self.fake_A_buffer.push_and_pop(fake_A)
                pred_fake = self.netD_A(fake_A.detach())
                loss_D_fake = self.loss_GAN(pred_real, self.label_fake)

                # total loss
                loss_D_A = (loss_D_real + loss_D_fake) * 0.5
                loss_D_A.backward()
                self.opt_DA.step()

                # B
                self.opt_DB.zero_grad()
                pred_real = self.netD_B(real_B)
                loss_D_real = self.loss_GAN(pred_real, self.label_real)

                fake_B = self.fake_B_buffer.push_and_pop(fake_B)
                pred_fake = self.netD_B(fake_B.detach())
                loss_D_fake = self.loss_GAN(pred_real, self.label_fake)

                # total loss
                loss_D_B = (loss_D_real + loss_D_fake) * 0.5
                loss_D_B.backward()
                self.opt_DB.step()

                print('loss_G: %.4f, loss_G_identity: %.4f, loss_G_GAN: %.4f, loss_G_cycle: %.4f,'
                    'loss_D_A: %.4f, loss_D_B: %.4f' % 
                    (loss_G.item(), (self.loss_identity_A + self.loss_identity_B).item(), 
                    (self.loss_GAN_A2B + self.loss_GAN_B2A).item(), (self.loss_cycle_ABA + self.loss_cycle_BAB).item(), 
                    loss_D_A.item(), loss_D_B.item()))

                self.writer_log.add_scalar('loss_G', loss_G, global_step=step)
                self.writer_log.add_scalar('loss_G_identity', (self.loss_identity_A + self.loss_identity_B), global_step=step)
                self.writer_log.add_scalar('loss_G_GAN', (self.loss_GAN_A2B + self.loss_GAN_B2A), global_step=step)
                self.writer_log.add_scalar('loss_G_cycle', (self.loss_cycle_ABA + self.loss_cycle_BAB), global_step=step)
                self.writer_log.add_scalar('loss_D_A', loss_D_A, global_step=step)
                self.writer_log.add_scalar('loss_D_B', loss_D_B, global_step=step)

                step += 1

            self.lr_scheduler_G.step()
            self.lr_scheduler_DA.step()
            self.lr_scheduler_DB.step()

            torch.save(self.netG_A2B.state_dict(), self.checkpoint_path + '/netG_A2B.pth')
            torch.save(self.netG_B2A.state_dict(),  self.checkpoint_path + '/netG_B2A.pth')
            torch.save(self.netD_A.state_dict(),  self.checkpoint_path + '/netD_A.pth')    
            torch.save(self.netD_B.state_dict(),  self.checkpoint_path + '/netD_B.pth')



if __name__=='__main__':
    pathA = ''
    pathB = ''
    checkpoint_path = ''
    trainer = Trainer(pathA, pathB, checkpoint_path)
    trainer.train()