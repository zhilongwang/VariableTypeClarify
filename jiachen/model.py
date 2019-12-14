import torch
import torch.nn as nn
import torch.nn.functional as F

class GRU_CNN(nn.Module):
    def __init__(self,vocab_size,emb_size,label_size,hidden_1,hidden_2,dropout,pt_embed=None):
        super(GRU_CNN,self).__init__()

        #self.word_embedding = nn.Embedding(vocab_size,emb_size)
        self.label_size = label_size

        #if pt_embed is not None:
            #self.word_embedding.weight.data.copy_(torch.from_numpy(pt_embed))
            #self.word_embedding.weight.requires_grad = False

        self.hidden_1 = hidden_1
        self.hidden_2 = hidden_2

        #self.dropout = nn.Dropout(p=dropout)

        self.conv = nn.Conv1d(2 * self.hidden_1,self.hidden_2,2)
        self.rnn = nn.GRU(emb_size,self.hidden_1,num_layers=1,bidirectional=True)

        self.linear = nn.Linear(self.hidden_2,self.label_size)

        #print(self.label_size)

    def forward(self,x):
        # GRU embedding
        #print(x.size())
        x,h = self.rnn(x)
        #print(x.size())
        x = x.permute(0,2,1)

        #print(x.size())

        # CNN
        x = self.conv(x)
        #print(x.size())
        x = F.relu(x)
        x = x.permute(0,2,1)
        x = x.max(1)[0]
        #print(x.size())
        #x = self.dropout(x)
        x = self.linear(x)
        #print(x.size())
        return x

    def get_trainable_parameters(self):
        trainable_params = []
        for param in self.parameters():
            if param.requires_grad:
                trainable_params.append(param)

        return trainable_params


class Text_CNN(nn.Module):
    def __init__(self,vocab_size,emb_size,label_size,output_channels,kernel_heights,kernel_width,dropout,pt_embed=None):
        super(Text_CNN,self).__init__()

        #self.word_embedding = nn.Embedding(vocab_size,emb_size,padding_idx=0)
        #if pt_embed is not None:
            #self.word_embedding.weight.data.copy_(torch.from_numpy(pt_embed))
            #self.word_embedding.weight.requires_grad = False

        input_dims = 1
        self.convs = nn.ModuleList([nn.Conv2d(input_dims,output_channels,(kh,kernel_width)) for kh in kernel_heights])

        #self.dropout = nn.Dropout(p=dropout)

        concated_out_channels = len(kernel_heights) * output_channels
        self.classifier = nn.Linear(concated_out_channels,label_size)

    def forward(self,x):
        #x = self.word_embedding(x)

        x = x.unsqueeze(dim=1)

        x = [F.relu(conv(x)).squeeze(dim=3) for conv in self.convs]

        x = [F.max_pool1d(i,i.size(2)).squeeze(dim=2) for i in x]

        x = torch.cat(x,dim=1)

        #x = self.dropout(x)

        logit = self.classifier(x)
        return logit

    def get_trainable_parameters(self):
        trainable_params = []
        for param in self.parameters():
            if param.requires_grad:
                trainable_params.append(param)

        return trainable_params

