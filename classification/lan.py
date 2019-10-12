import numpy as np
import tensorflow as tf
print(tf.__version__)
import time
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

from tensorflow.keras.layers import GRUCell
from tensorflow.keras.layers import LSTMCell
from tensorflow.keras.layers import SimpleRNNCell
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import RNN
from tensorflow.keras.layers import Dense

from config import config
from util import utils
import random
#import pdb

class VariableType(tf.keras.Model):
    def __init__(self):
        super(VariableType, self).__init__(name='')
        self.config = config
        self.cell_type = config['cell_type']
        self.depth = config['depth']
        self.is_birnn = config['birnn']
        self.class_num = config['class_num']
        self._dtype = tf.float16 if config['use_fp16'] else tf.float32        
        self.use_residual = config['use_residual']
        self.batch_size = config['batch_size']
        self.hidden_units = config['hidden_units']#len(config['voc'])#config['hidden_units']
        self.optimizer = config['optimizer']
        self.learning_rate = config['learning_rate']
        self.max_gradient_norm = config['max_gradient_norm']
        self.instruction_number = config['instruction_number']
        self.use_dropout = True
        self.init_variables()
        self.init_model()
        self.init_optimizer()

    def init_variables(self):
        self.attention_context = tf.Variable(tf.random.truncated_normal([self.hidden_units, 1]), dtype=self._dtype)

    def init_model(self):
        self.rnn = LSTM(self.hidden_units, return_state=False, return_sequences=True)
        self.output_layer = Dense(self.class_num)
        
    def init_optimizer(self):
        if self.optimizer.lower() == 'adadelta':
            self.opt = tf.optimizers.Adadelta(learning_rate=self.learning_rate)
        elif self.optimizer.lower() == 'adam':
            self.opt = tf.optimizers.Adam(learning_rate=self.learning_rate)
        elif self.optimizer.lower() == 'rmsprop':
            self.opt = tf.optimizers.RMSprop(learning_rate=self.learning_rate)
        else:
            self.opt = tf.optimizers.SGD(learning_rate=self.learning_rate)
        return self.opt

    def call(self, inputs):
        inputs_embedded = tf.cast(inputs, dtype=self._dtype)
        outputs = self.rnn(inputs_embedded)
        attention_r = self.attention(outputs)
        logits = self.output_layer(attention_r)
        return logits

    def pred(self, logits):
        return tf.argmax(tf.nn.softmax(logits),1)

    def attention(self, inputs):
        return tf.reshape(tf.matmul(tf.reshape(tf.nn.softmax(tf.reshape(tf.matmul(tf.reshape(tf.tanh(inputs), [-1, self.hidden_units]),self.attention_context),[self.batch_size, -1])),[self.batch_size,1, -1]), inputs),[self.batch_size, self.hidden_units])

def test(test_img, test_lab, path):
  vt_model = VariableType()
  vt_model.compile(loss='sparse_categorical_crossentropy',
              optimizer=vt_model.opt, metrics= ['accuracy'])
  try:
    print('loading ...')
    vt_model.load_weights(path)
  except:
    return
  test_img = tf.cast(test_img, dtype=tf.float32)
  test_lab = tf.cast(test_lab, dtype=tf.float32) 
  pred = vt_model.predict(test_img, batch_size=config['batch_size'])
  print(vt_model.pred(pred), test_lab)

# Initialize model using CPU
def train(train_images, train_labels, test_img, test_lab, path):
  vt_model = VariableType()
  vt_model.compile(loss='sparse_categorical_crossentropy',
              optimizer=vt_model.opt, metrics= ['accuracy'])
  try:
    print('loading ...')
    vt_model.load_weights(path)
  except:
    pass
  cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=path, save_weights_only=True, verbose=1)
  time_start = time.time()
  train_images = tf.cast(train_images, dtype=tf.float32)
  train_labels = tf.cast(train_labels, dtype=tf.float32)
  test_img = tf.cast(test_img, dtype=tf.float32)
  test_lab = tf.cast(test_lab, dtype=tf.float32)
  history = vt_model.fit(train_images, train_labels, batch_size=config['batch_size'], shuffle= True, validation_data=(test_img,test_lab), callbacks=[cp_callback], epochs = config['max_epochs'])#, True , config['dropout_prob']) 
  pred = vt_model.predict(test_img, batch_size=config['batch_size'])
  #print(vt_model.pred(pred), test_lab)
  time_taken = time.time() - time_start
  print('\nTotal time taken (in seconds): {:.2f}'.format(time_taken))

def readData():
    train_seqs, train_labels = utils.Lan_features(config['input'])
    train_seqs = utils.padding_feature(train_seqs, config['instruction_number'], config['instruction_length'], '90')
    test_seqs, test_labels = utils.Lan_features(config['valid'])
    test_seqs = utils.padding_feature(test_seqs, config['instruction_number'], config['instruction_length'], '90')
    print(test_seqs, test_labels )
    if len(train_seqs) % config['batch_size'] != 0:
        rand = [random.randint(0,len(train_seqs)-1) for i in range(config['batch_size'] - len(train_seqs) % config['batch_size'])]
        for r in rand:
            train_seqs.append(train_seqs[r])
            train_labels = np.append(train_labels,train_labels[r])
    if len(test_seqs) % config['batch_size'] != 0:
        rand = [random.randint(0,len(test_seqs)-1) for i in range(config['batch_size'] - len(test_seqs) % config['batch_size'])]
        for r in rand:
            test_seqs.append(test_seqs[r])
            test_labels = np.append(test_labels,test_labels[r])
    return train_seqs, train_labels, test_seqs, test_labels 

train_seqs, train_labels, test_seqs, test_labels = readData()
train(train_seqs, train_labels, test_seqs, test_labels, config['save_path'])
test(test_seqs, test_labels, config['save_path'])
