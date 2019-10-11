import re

def readRaw(filename):
  with open(filename, 'r') as f:
    raw = f.read()
  return raw.split('\n\n')

def extractLabel(raw):
  labels = []
  for line in raw:
    label = re.findall(r'label: (.+)', line)
    labels.append(label)
  return labels

def extractAssemblyCode(raw):
  seqs = []
  for line in raw:
    seq = [''.join(i.strip('\t').split(' ')) for i in re.findall(r'((?:[a-z0-9]{2}\ ){1,}\t)',line)]
    seqs.append(seq)
  return seqs

def extractOpcode(raw):
  codes = []
  for line in raw:
    codes.append(re.findall(r'\t(.+)\t', line))
  return codes

def Lan_features(filename):
  raw  = readRaw(filename)
  return extractAssemblyCode(raw), extractLabel(raw)

if __name__ == '__main__':
  print(Lan_features('/home/lfz5092/Lan/IST597/VariableTypeClarify/classification/data/rawdata.txt'))
