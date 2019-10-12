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

    def call(self, inputs_embedded, y_train, training=True, dropout=0.):
        self.dropout = dropout

        with tf.GradientTape() as tape:
            inputs_embedded = tf.cast(inputs_embedded, dtype=self._dtype)
            outputs = self.rnn(inputs_embedded)
            attention_r = self.attention(outputs)
            logits = self.output_layer(attention_r)
            self.loss = self.cal_loss(logits, y_train)
            pred = self.pred(logits)
            
        def cal_grad():
            print('calculate gradient...')
            self._variables = self.trainable_variables
            grads = tape.gradient(self.loss, self._variables)
            clip_gradients, _ = tf.clip_by_global_norm(grads, self.max_gradient_norm)
            self.opt.apply_gradients(zip(clip_gradients, self._variables))
            print(logits, self.loss, pred)
            return logits, self.loss, pred
      
        def cal_not_grad():
            print('return...')
            return logits, self.loss, pred
    
        return tf.cond(train, true_fn = cal_grad, false_fn = cal_not_grad)

    def pred(self, logits):
        return tf.argmax(tf.nn.softmax(logits),1)

    def metircs(self):
        return keras.metrics.SparseCategoricalAccuracy()

    def cal_loss(self, logits, y_true):
        return tf.nn.sparse_softmax_cross_entropy_with_logits(logits = logits,labels = y_true)        

    def attention(self, inputs):
        return tf.reshape(tf.matmul(tf.reshape(tf.nn.softmax(tf.reshape(tf.matmul(tf.reshape(tf.tanh(inputs), [-1, self.hidden_units]),self.attention_context),[self.batch_size, -1])),[self.batch_size,1, -1]), inputs),[self.batch_size, self.hidden_units])

def test(img, lab, path):
    _model = tf.keras.models.load_model(path)
    acc_avg = tf.metrics.Accuracy()
    loss_avg = tf.metrics.Mean()
    test_ds = tf.data.Dataset.from_tensor_slices((img, lab)).shuffle(1000, seed=2612).batch(batch_size,drop_remainder=True)
    for ids,(_x,_y) in test_ds.enumerate():
      logits,loss,pred = _model(_x, _y, False, dropout = 0.)
      loss_avg(loss)
      acc_avg(pred, _y)
    return loss_avg.result(), acc_avg.result()

# Initialize model using CPU
def train(train_images, train_labels, test_img, test_lab, path):
  if tf.saved_model.contains_saved_model(path):
    print('load model:' + path)
    vt_model = tf.keras.models.load_model(path)
  else:
    print('create new model')
    vt_model = VariableType()
    #vt_model.compile(optimizer = vt_model.opt, loss= vt_model.cal_loss, metrics = [vt_model.metircs])
  time_start = time.time()
  train_loss_results = []
  train_accuracy_results = []
  test_loss_results = []
  test_accuracy_results = []
  for epoch in range(config['max_epochs']):
    train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels)).shuffle(1000).batch(config['batch_size'],drop_remainder=True)
    acc_avg = tf.metrics.Accuracy()
    loss_avg = tf.metrics.Mean()
    for inputs, outputs in train_ds:
        logits,loss,pred = vt_model(inputs, outputs, True , config['dropout_prob'])
        loss_avg(loss)
        acc_avg(pred, outputs)
    #vt_model.save(path)
    #l, a = test(test_img, test_lab, path)
    l, a = 0,1
    print('Number of Epoch = {} - Average MSE:= {:.10f} - ACC:={:.4f}; TEST Loss:={:.10f} - ACC:={:.4f}'.format(
        epoch + 1, loss_avg.result(), acc_avg.result(), l, a))
    test_loss_results.append(l)
    test_accuracy_results.append(a)
    train_loss_results.append(loss_avg.result())
    train_accuracy_results.append(acc_avg.result())
  time_taken = time.time() - time_start
  vt_model.save(path)

  print('\nTotal time taken (in seconds): {:.2f}'.format(time_taken))
  return test_loss_results, test_accuracy_results, train_loss_results, train_accuracy_results

def readData():
    train_seqs, train_labels = utils.Lan_features(config['input'])
    train_seqs = utils.padding_feature(train_seqs, config['instruction_number'], config['instruction_length'], '90')
    test_seqs, test_labels = utils.Lan_features(config['valid'])
    test_seqs = utils.padding_feature(test_seqs, config['instruction_number'], config['instruction_length'], '90')
    return train_seqs, train_labels, test_seqs, test_labels 

train_seqs, train_labels, test_seqs, test_labels = readData()
train(train_seqs, train_labels, test_seqs, test_labels, config['save_path'])
