import os

config = {}

config['cell_type'] = 'gru'
config['birnn'] = True
config['use_fp16'] = False
config['batch_size'] = 500
config['hidden_units'] = 64
config['optimizer'] = 'adam'
config['learning_rate'] = 0.003
config['max_gradient_norm'] = 1.0
config['max_epochs'] = 200
config['dropout_prob'] = 0.4
config['loss_func'] = 1
config['save_path'] = 'model/lan/1/'
#TODO
config['input'] = os.getcwd() + '/data/'
config['valid'] = os.getcwd() + '/data/'
config['class_num'] = 6
config['instruction_number'] = 20
config['instruction_length'] = 10
