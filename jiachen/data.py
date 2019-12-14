import os
import os.path as osp
import numpy as np
import tqdm
import re

CLASSES = ['upointer', 'Unknow', 'unsigned int', 'int', 'char', '_Bool']

def load_data_old(data_pth,data_ext):
    raw_data = []
    raw_label = []

    for file_name in tqdm.tqdm(os.listdir(data_pth)):
        if osp.splitext(file_name)[-1] == data_ext:
            with open(osp.join(data_pth,file_name)) as fp:
                for line in fp:
                    line = line.strip()
                    if len(line.split(' ')) <= 2:
                        cur_label = line
                    else:
                        valid_line = []
                        for tok in line.split(' '):
                            if tok == '':
                                break
                            valid_line.append(tok)
                        raw_data.append(valid_line)
                        raw_label.append(cur_label)

    assert len(raw_data) == len(raw_label)

    print('Loading Raw Data Finished..')
    #print(set(raw_label))

    return raw_data,raw_label

def filter_invalid(data_pth,data_ext):
    invalid_files = []
    for file_name in tqdm.tqdm(os.listdir(data_pth)):
        if osp.splitext(file_name)[-1] == data_ext:
            with open(osp.join(data_pth,file_name),'r') as fp:
                if len(fp.readlines()) == 0:
                    invalid_files.append(file_name)

    return invalid_files

def load_data(data_pth,data_ext):
    raw_data = []
    raw_label = []

    invalid_files = filter_invalid(data_pth,data_ext)

    for file_name in tqdm.tqdm(os.listdir(data_pth)):
        if file_name in invalid_files:
            continue
        if osp.splitext(file_name)[-1] == data_ext:
            with open(osp.join(data_pth,file_name),'r') as fp:
                for idx,line in enumerate(fp):
                    line = line.strip()
                    if line in CLASSES:
                        raw_label.append(line)
                        if not idx == 0:
                            assert len(seqs) > 0
                            raw_data.append(seqs)
                        seqs = []
                    else:
                        items = []
                        for tok in line.split(' '):
                            if tok == '':
                                break
                            items.append(tok)
                        seqs += items
                raw_data.append(seqs)

    assert len(raw_data) == len(raw_label)
    return raw_data,raw_label



def parse_data(raw_data):
    seqs = []
    for item in raw_data:
        #seq = [item.strip('\t') for i in re.findall(r'((?:[a-z0-9]{2}\ ){1,}\t)',line)]
        seq = ['{:08b}'.format(int(token,16)) for token in item]
        seqs.append(seq)

    return seqs


def parse_label(raw_label):
    labels = set(raw_label)
    label_size = len(labels)
    #one_hot = np.eye(label_size)
    label_to_id = {label:label_id for label,label_id in zip(labels,range(label_size))}
    parsed_labels = [label_to_id[label] for label in raw_label]

    return parsed_labels

def get_onehot(labels):
    uni_labels = set(labels)
    label_size = len(uni_labels)
    one_hot = np.eye(label_size)
    one_hot_labels = [one_hot[label_id] for label_id in labels]
    one_hot_labels = np.array(one_hot_labels)
    return one_hot_labels



def get_pad_length(parsed_data):
    max_seq_len = 0
    max_feat_len = 0
    for seq in parsed_data:
        if len(seq) > max_seq_len:
            max_seq_len = len(seq)
        for item in seq:
            if len(item) > max_feat_len:
                max_feat_len = len(item)
    return max_seq_len,max_feat_len

def pad_feature(parsed_data,padding_ext='90',global_padding=True):
    if global_padding:
        max_seq_len,feat_len = get_pad_length(parsed_data)

    print(max_seq_len,feat_len)
    new_data = []
    padding_feat = '{:08b}'.format(int(padding_ext,16))
    for seq in tqdm.tqdm(parsed_data):
        pad_seq_len = max_seq_len - len(seq)
        for item in seq:
            pad_feat_len = max_seq_len - len(item)
            #if pad_feat_len > 0:
                #item.extend([padding_feat for _ in range(pad_feat_len)])
        if pad_seq_len > 0:
            seq.extend([padding_feat for _ in range(pad_seq_len)])
        new_data.append([[int(token) for token in item] for item in seq])

    print('Feature Padding finished..')

    return new_data,feat_len
