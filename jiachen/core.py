import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import tqdm

from sklearn.metrics import roc_auc_score

def train_epoch(model,batch_size,training_data,optimizer,criterion,onehot_labels):
    model.train()
    aver_loss = 0
    preds,tgts = [],[]
    correct = 0
    for batch in tqdm.tqdm(training_data):
        data,tgt = batch
        data = data.float().cuda()
        tgt = tgt.cuda()
        optimizer.zero_grad()
        pred = model(data)
        loss = criterion(pred,tgt)
        loss.backward()
        optimizer.step()

        correct += torch.argmax(pred,dim=-1).eq(tgt).sum().item()

        preds.append(F.sigmoid(pred).data.cpu().numpy())

        aver_loss += loss.item()

    #print(onehot_labels.shape)
    #print(np.vstack(preds).shape)

    auc_score = roc_auc_score(onehot_labels,np.vstack(preds))

    total = len(training_data) * batch_size
    accuracy = correct / total

    aver_loss /= len(training_data)

    return aver_loss,accuracy,auc_score

def eval_epoch(model,batch_size,validation_data,criterion,onehot_labels):
    model.eval()
    aver_loss = 0
    correct = 0
    preds,tgts = [],[]
    for batch in tqdm.tqdm(validation_data):
        data,tgt = batch
        data = data.float().cuda()
        tgt = tgt.cuda()
        pred = model(data)
        loss = criterion(pred,tgt)

        preds.append(F.sigmoid(pred).data.cpu().numpy())

        correct += torch.argmax(pred,dim=-1).eq(tgt).sum().item()
        #preds.append(torch.argmax(F.sigmoid(pred)).data.cpu().numpy())
        #tgts.append(tgt.data.cpu().numpy())

        aver_loss += loss.item()

    total = len(validation_data) * batch_size
    accuracy = correct / total

    #print(one_hot_labels.shape)
    #print(np.vstack(preds).shape)

    auc_score = roc_auc_score(onehot_labels,np.vstack(preds))
    #accuracy = np.sum([prob == tgt for prob,tgt in zip(np.vstack(preds),np.vstack(tgts))]) / (len(training_data) * batch_size)

    aver_loss /= len(validation_data)

    return aver_loss,accuracy,auc_score

