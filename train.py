from model import Model
import numpy as np
import os
import torch
from torchvision.datasets import mnist
from torch.nn import CrossEntropyLoss
from torch.optim import SGD
from torch.utils.data import DataLoader
from torchvision import transforms

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    batch_size = 256
    transform = transforms.Compose([transforms.ToTensor(), 
                                    transforms.Normalize((0.5,), (0.5,))])
    train_dataset = mnist.MNIST(root='./train', train=True, transform=transform, download=True)
    test_dataset = mnist.MNIST(root='./test', train=False, transform=transform, download=True)
    train_loader = DataLoader(train_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    model = Model().to(device)
    optimizer = SGD(model.parameters(), lr=1e-1)
    criterion = CrossEntropyLoss()
    num_epochs = 3
    prev_acc = 0
    for current_epoch in range(num_epochs):
        model.train()
        for idx, (train_x, train_label) in enumerate(train_loader):
            train_x = train_x.to(device)
            train_label = train_label.to(device)
            optimizer.zero_grad()
            predict_y = model(train_x.float())
            loss = criterion(predict_y, train_label.long())
            loss.backward()
            optimizer.step()

        all_correct_num = 0
        all_sample_num = 0
        model.eval()
        
        for idx, (test_x, test_label) in enumerate(test_loader):
            test_x = test_x.to(device)
            test_label = test_label.to(device)
            predict_y = model(test_x.float()).detach()
            predict_y =torch.argmax(predict_y, dim=-1)
            current_correct_num = predict_y == test_label
            all_correct_num += np.sum(current_correct_num.to('cpu').numpy(), axis=-1)
            all_sample_num += current_correct_num.shape[0]
        acc = all_correct_num / all_sample_num
        print('accuracy: {:.3f}'.format(acc), flush=True)
        if not os.path.isdir("models"):
            os.mkdir("models")
        torch.save(model, 'models/mnist_{:.3f}.pkl'.format(acc))
        if np.abs(acc - prev_acc) < 1e-4:
            break
        prev_acc = acc
    print("Model finished training")
