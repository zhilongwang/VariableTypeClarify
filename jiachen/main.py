import os
import os.path as osp
import time

import argparse
import tqdm
import random
import sys
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from sklearn.model_selection import KFold

import config as cfg

from collections import defaultdict

from data import get_onehot,load_data,parse_data,parse_label,pad_feature,CLASSES
from model import GRU_CNN,Text_CNN
from dataset import Dataset
from core import train_epoch,eval_epoch

sys.path.insert(0,osp.join(osp.dirname(osp.abspath(__file__))))

#torch.backends.cudnn.enabled = False

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp_name',required=True,help='experiment result saving path')

    parser.add_argument('--epoch',type=int,default=10)
    parser.add_argument('--batch_size',type=int,default=512)
    parser.add_argument('--model',type=str,default='GRU_CNN')
    parser.add_argument('--cuda',action='store_true')

    args = parser.parse_args()

    # data parser

    raw_data,raw_label = load_data(cfg.data_root,cfg.data_ext)

    seqs = parse_data(raw_data)
    labels = parse_label(raw_label)

    onehot_labels = get_onehot(labels)

    padded_seqs,embed_size = pad_feature(seqs,padding_ext=cfg.padding_ext,global_padding=cfg.padding_all)

    padded_seqs = np.array(padded_seqs)
    labels = np.array(labels)

    data_size = len(padded_seqs)
    label_size = len(set(labels))

    data_idxs = list(range(data_size))

    training_split = 0.7

    train_idx = random.sample(data_idxs,int(data_size * training_split))

    train_dict = defaultdict(int)
    for idx in train_idx:
        train_dict[idx] = 1

    val_idx = [idx for idx in data_idxs if not train_dict[idx] == 1]

    train_onehot = np.array([onehot_labels[idx] for idx in train_idx])
    val_onehot = np.array([onehot_labels[idx] for idx in val_idx])

    train_dataset = Dataset(padded_seqs,labels,train_idx,mode='train')
    val_dataset = Dataset(padded_seqs,labels,val_idx,mode='val')

    train_loader = DataLoader(train_dataset,batch_size=args.batch_size,shuffle=True,num_workers=cfg.num_workers)
    val_loader = DataLoader(val_dataset,batch_size=args.batch_size,shuffle=False,num_workers=cfg.num_workers)

    criterion = nn.CrossEntropyLoss()

    if args.cuda:
        criterion = criterion.cuda()

    if args.model == 'GRU_CNN':
        model = GRU_CNN(vocab_size = data_size,
                emb_size = embed_size,
                label_size = label_size,
                hidden_1 = cfg.hidden_1,
                hidden_2 = cfg.hidden_2,
                pt_embed = None,
                dropout = cfg.dropout)

    elif args.model == 'Text_CNN':
        model = Text_CNN(vocab_size = data_size,
                emb_size = embed_size,
                output_channels = cfg.kernel_dims,
                kernel_heights = cfg.kernel_heights,
                kernel_width = embed_size,
                label_size = label_size,
                pt_embed = None,
                dropout = cfg.dropout)

    else:
        raise NotImplementedError

    if args.cuda:
        model = model.cuda()

    optimizer = torch.optim.Adam(model.get_trainable_parameters(),lr=cfg.learning_rate,betas=cfg.betas,eps=cfg.eps)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,factor=0.2,patience=2,verbose=1)

    best_acc = 0
    for epoch in range(args.epoch):
        train_loss,train_acc,train_auc = train_epoch(model,args.batch_size,train_loader,optimizer,criterion,train_onehot)
        val_loss,val_acc,val_auc = eval_epoch(model,args.batch_size,val_loader,criterion,val_onehot)
        scheduler.step(val_loss)

        print('[training][Epoch:{epoch}] loss:{loss:.3f} accu:{accu:.3f} auc:{auc:.3f}'.format(epoch=epoch,loss=train_loss,accu=train_acc,auc=train_auc))
        print('[validation][Epoch:{epoch}] loss:{loss:.3f} accu:{accu:.3f} auc:{auc:.3f}'.format(epoch=epoch,loss=val_loss,accu=val_acc,auc=val_auc))

        ckpt = dict(model = model.state_dict(),
                settings = args,
                epoch = epoch,
                optim = optimizer,
                accu = val_acc
                )

        if val_acc > best_acc:
            best_acc = val_acc
            best_model = model
            save_dir = osp.join(cfg.model_dir,args.exp_name)
            if not osp.exists(save_dir):
                os.makedirs(save_dir)

            torch.save(ckpt,osp.join(save_dir,'epoch_' + str(epoch) + '.ckpt'))

    print('Best acc:{:.3f}'.format(best_acc))


if __name__ == '__main__':
    main()
