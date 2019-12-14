import torch
import numpy as np
from torch.utils import data

class Dataset(data.Dataset):
    def __init__(self,data,tgt,data_idxs,mode):
        self.mode = mode
        self.sampled_data = [data[idx] for idx in data_idxs]
        self.sampled_tgt = [tgt[idx] for idx in data_idxs]

        #sampled_tgt = np.array(self.sampled_tgt)

        assert len(self.sampled_data) == len(self.sampled_tgt)

    def __getitem__(self,idx):
        data = self.sampled_data[idx]
        tgt = self.sampled_tgt[idx]

        return data,tgt

    def __len__(self):
        return len(self.sampled_data)
