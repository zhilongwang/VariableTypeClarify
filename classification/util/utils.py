import re
import numpy as np

'''
def readRaw(filename):
  with open(filename, 'r') as f:
    raw = f.read()
  return raw.split('\n\n')

def extractLabel(raw):
  labels = []
  for line in raw:
    label = re.findall(r'label: (.+)', line)
    labels.append(label)
  lookupTable, indexed_dataSet = np.unique(np.array(labels), return_inverse=True)
  print('lookupTable', lookupTable)
  return indexed_dataSet

def extractAssemblyCode(raw):
  seqs = []
  for line in raw:
    seq = [i.strip(' \t') for i in re.findall(r'((?:[a-z0-9]{2}\ ){1,}\t)',line)]
    seqs.append(seq)
  return seqs

def extractOpcode(raw):
  codes = []
  for line in raw:
    codes.append(re.findall(r'\t(.+)\t', line))
  return codes
'''

import glob

def readRaw(dirs):
  fns = glob.glob(dirs+'*.out')
  labels = []
  seqs = []
  codes = []
  _tmp_seq = []
  _tmp_code = []
  for fn in fns:
    with open(fn, 'r') as f:
      raw = f.read()
      for line in raw.split('\n'):
        if len(line) == 0:
          continue
        if line.find('  ') == -1:
           if len(_tmp_seq) != 0 or len(_tmp_code) != 0:
              seqs.append(_tmp_seq)
              codes.append(_tmp_code)
           _tmp_seq = []
           _tmp_code = []
           labels.append(line)
        elif len(line) < 30:
           continue
        else:
           seq = [i.strip(' ') for i in re.findall(r'((?:[a-z0-9]{2}\ ){1,})',line[:30])]
           _tmp_seq.extend(seq)
           _tmp_code.append(re.findall(r'([^ ]+) ',line[30:])[0])
  if len(_tmp_seq) != 0 or len(_tmp_code) != 0:
     seqs.append(_tmp_seq)
     codes.append(_tmp_code)
  return labels, seqs, codes

import os
import pickle
def Lan_features(filename):
  if os.path.exists('features.b'):
    labels, seqs, codes = pickle.load(open('features.b','rb'))
  else:
    labels, seqs, codes  = readRaw(filename)
    pickle.dump((labels, seqs, codes),open('features.b','wb'))
  return seqs, codes, labels#extractAssemblyCode(raw), extractLabel(raw)

def padding_feature(seqs, length, sub_length, end_token):
  end_token = '{:08b}'.format(int(end_token,16))
  max_length = 0
  max_sub_length = 0
  newseqs = []
  for seq in seqs:
    newseq = []
    for s in seq:
      s = s.split(' ')
      s = ['{:08b}'.format(int(token,16)) for token in s]
      max_sub_length = max_sub_length if max_sub_length > len(s) else len(s)
      s.extend([end_token for _ in range(sub_length - len(s))])
      newseq.append(''.join(s))
    max_length = max_length if max_length > len(newseq) else len(newseq)
    if length > len(newseq):
      newseq.extend([''.join([end_token for _ in range(sub_length)]) for _ in range(length - len(newseq))])
    newseqs.append([list(map(int, s)) for s in newseq])
  print('max instruction numbers:', max_length, ';max length of instruction:', max_sub_length)
  assert max_length <= length
  assert max_sub_length <= sub_length
  return newseqs

if __name__ == '__main__':
  #print(Lan_features('/home/lfz5092/Lan/IST597/VariableTypeClarify/classification/data/rawdata.txt'))
  print(readRaw('/home/lfz5092/Lan/IST597/VariableTypeClarify/classification/data/'))

