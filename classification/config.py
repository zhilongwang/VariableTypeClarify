import os

config = {}

config['cell_type'] = 'gru'
config['depth'] = 1
config['birnn'] = False
config['use_fp16'] = False
config['use_residual'] = True
config['batch_size'] = 2
config['hidden_units'] = 128
config['optimizer'] = 'adam'
config['learning_rate'] = 0.003
config['max_gradient_norm'] = 1.0
config['max_epochs'] = 100
config['dropout_prob'] = 0.
config['save_path'] = 'model/test/'
#TODO
config['input'] = os.getcwd() + '/data/rawdata.txt'
config['valid'] = os.getcwd() + '/data/rawdata.txt'
config['class_num'] = 4
config['instruction_number'] = 20
config['instruction_length'] = 10