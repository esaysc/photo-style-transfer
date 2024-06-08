import torch
from torch.optim import Optimizer

class MyModel:
    def __init__(self, device, n_epoch, dataloader, lr_scheduler_G, lr_scheduler_DA, lr_scheduler_DB):
        super().__init__()
    # 假设类的其他部分已经定义

    def train(self):
        # training loop
        for epoch in range(n_epoch):
            print('Epoch: %d' % epoch)
            for i, batch in enumerate(dataloader):
                self.train_generator(batch)
                self.train_discriminator(batch)

            lr_scheduler_G.step()
            lr_scheduler_DA.step()
            lr_scheduler_DB.step()

            self.save_models()

    def train_generator(self, batch):
        real_A, real_B = self.preprocess(batch)

        opt_G.zero_grad()

        same_B, loss_identity_B = self.compute_loss_identity(real_B)
        same_A, loss_identity_A = self.compute_loss_identity(real_A)

        fake_B, pred_fake = self.forward_pass(real_A, netG_A2B, netD_B)
        loss_GAN_A2B = self.compute_loss_GAN(pred_fake, label_real)

        fake_A, pred_fake = self.forward_pass(real_B, netG_B2A, netD_A)
        loss_GAN_B2A = self.compute_loss_GAN(pred_fake, label_real)

        recovered_A, _ = self.forward_pass(fake_B, netG_B2A, None)
        loss_cycle_ABA = self.compute_loss_cycle(recovered_A, real_A)

        recovered_B, _ = self.forward_pass(fake_A, netG_A2B, None)
        loss_cycle_BAB = self.compute_loss_cycle(recovered_B, real_B)

        loss_G = loss_identity_A + loss_identity_B + loss_GAN_A2B + loss_GAN_B2A + loss_cycle_ABA + loss_cycle_BAB
        loss_G.backward()
        opt_G.step()

        self.log_training_loss(loss_G, loss_identity_A, loss_identity_B, 
                                loss_GAN_A2B, loss_GAN_B2A, loss_cycle_ABA, loss_cycle_BAB)

    def train_discriminator(self, batch):
        real_A, real_B = self.preprocess(batch)

        opt_DA.zero_grad()
        opt_DB.zero_grad()

        pred_real_A, loss_D_real_A = self.compute_loss_D(real_A, netD_A)
        pred_fake_A, _ = self.compute_loss_D(fake_A_buffer.push_and_pop(fake_A), netD_A, detach=True)
        loss_D_A = (loss_D_real_A + pred_fake_A) * 0.5
        loss_D_A.backward()
        opt_DA.step()

        pred_real_B, loss_D_real_B = self.compute_loss_D(real_B, netD_B)
        pred_fake_B, _ = self.compute_loss_D(fake_B_buffer.push_and_pop(fake_B), netD_B, detach=True)
        loss_D_B = (loss_D_real_B + pred_fake_B) * 0.5
        loss_D_B.backward()
        opt_DB.step()

        self.log_training_loss(loss_D_A, loss_D_B)

    def preprocess(self, batch):
        real_A = batch['A'].to(device)
        real_B = batch['B'].to(device)
        return real_A, real_B

    def compute_loss_identity(self, real):
        same = netG_A2B(real) if 'A' in real else netG_B2A(real)
        loss = loss_identity(same, real) * 5.0
        return same, loss

    def forward_pass(self, real, generator, discriminator):
        fake = generator(real)
        pred_fake = discriminator(fake) if discriminator else None
        return fake, pred_fake

    def compute_loss_GAN(self, pred_fake, label):
        return loss_GAN(pred_fake, label)

    def compute_loss_cycle(self, recovered, real):
        return loss_cycle(recovered, real) * 10.0

    def compute_loss_D(self, sample, discriminator, detach=False):
        pred = discriminator(sample)
        loss = loss_GAN(pred, label_real) if detach else loss_GAN(pred, label_fake)
        return pred, loss

    def log_training_loss(self, *losses):
        print(' '.join(f'loss_{loss_name}: {loss.item():.4f}' for loss_name, loss in zip(loss_names, losses)))

    def save_models(self):
        torch.save(netG_A2B.state_dict(), 'checkpoints/netG_A2B.pth')
        torch.save(netG_B2A.state_dict(), 'checkpoints/netG_B2A.pth')
        torch.save(netD_A.state_dict(), 'checkpoints/netD_A.pth')
        torch.save(netD_B.state_dict(), 'checkpoints/netD_B.pth')