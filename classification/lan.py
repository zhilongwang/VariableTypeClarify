import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
from tensorflow.keras.layers import GRU
from tensorflow.keras.layers import RNN
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.layers import Dense

from config import config
from util import utils
import random
#import pdb

class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
  def __init__(self, d_model, warmup_steps=4000):
    super(CustomSchedule, self).__init__()
    
    self.d_model = d_model
    self.d_model = tf.cast(self.d_model, tf.float32)

    self.warmup_steps = warmup_steps
    
  def __call__(self, step):
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps ** -1.5)
    
    return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)
    
class VariableType(tf.keras.Model):
    def __init__(self):
        super(VariableType, self).__init__(name='')
        self.config = config
        self.cell_type = config['cell_type']
        self.is_birnn = config['birnn']
        self.class_num = config['class_num']
        self._dtype = tf.float16 if config['use_fp16'] else tf.float32  
        self.batch_size = config['batch_size']
        self.hidden_units = config['hidden_units']
        self.optimizer = config['optimizer']
        self.learning_rate = CustomSchedule(self.hidden_units)#config['learning_rate']
        self.max_gradient_norm = config['max_gradient_norm']
        self.instruction_number = config['instruction_number']
        self.dropout_porb = config['dropout_prob']
        self.loss_func = config['loss_func']
        self.train_loss = tf.keras.metrics.Mean(name='train_loss')
        self.train_accuracy = tf.keras.metrics.CategoricalAccuracy(name='train_accuracy')
        self.init_variables()
        self.init_model()
        self.init_optimizer()

    def init_variables(self):
        self.attention_context = tf.Variable(tf.random.truncated_normal([self.hidden_units, 1]), dtype=self._dtype)

    def init_model(self):
        self.rnn = LSTM(self.hidden_units, return_state=False, return_sequences=True)
        if self.cell_type == 'gru':
            self.rnn = GRU(self.hidden_units, return_state=False, return_sequences=True)
        elif self.cell_type == 'rnn':
            self.rnn = RNN(self.hidden_units, return_state=False, return_sequences=True)
        if self.is_birnn:
            self.rnn = Bidirectional(self.rnn, merge_mode = 'sum')
        self.dropout_layer1 = tf.keras.layers.Dropout(self.dropout_porb)
        self.dropout_layer2 = tf.keras.layers.Dropout(self.dropout_porb)
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        #self.layernorm3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.output_layer = Dense(self.class_num)   

    def init_optimizer(self):
        if self.optimizer.lower() == 'adadelta':
            self.opt = tf.optimizers.Adadelta(learning_rate=self.learning_rate, clipnorm=self.max_gradient_norm)
        elif self.optimizer.lower() == 'adam':
            self.opt = tf.optimizers.Adam(learning_rate=self.learning_rate, clipnorm=self.max_gradient_norm)
        elif self.optimizer.lower() == 'rmsprop':
            self.opt = tf.optimizers.RMSprop(learning_rate=self.learning_rate, clipnorm=self.max_gradient_norm)
        else:
            self.opt = tf.optimizers.SGD(learning_rate=self.learning_rate, clipnorm=self.max_gradient_norm)
        return self.opt
    
    def forword(self, inputs, training):
        inputs_embedded = tf.cast(inputs, dtype=self._dtype)
        outputs = self.rnn(inputs_embedded)
        outputs = self.dropout_layer1(outputs, training = training)
        outputs = self.layernorm1(outputs)
        #outputs = tf.cond(self.use_dropout, lambda: self.dropout_layer(outputs), lambda: outputs)
        outputs = self.attention(outputs)
        outputs = self.dropout_layer2(outputs, training = training)
        outputs = self.layernorm2(outputs)
        logits = self.output_layer(outputs) 
        return logits      

    def cal_loss(self, logits, y_true):
        if self.loss_func == 1:
            return tf.keras.losses.sparse_categorical_crossentropy(y_true, logits, from_logits=True)
        
    def call(self, inputs, y_true, training):
        #self.use_dropout = tf.cast(training, dtype=tf.bool)
        #print('train...', self.use_dropout)
        with tf.GradientTape() as tape:
            logits = self.forword(inputs, training)
            loss = self.cal_loss(logits, y_true)
            pred = self.pred(logits)
            self.train_loss(loss)
            self.train_accuracy(y_true, pred)

        def cal_grad():
            gradients = tape.gradient(loss, self.trainable_variables)    
            self.opt.apply_gradients(zip(gradients, self.trainable_variables))
            return logits, loss, pred
        
        def cal_not_grad():
            return logits, loss, pred
      
        return tf.cond(training, true_fn = cal_grad, false_fn = cal_not_grad)

    def pred(self, logits):
        return tf.argmax(tf.nn.softmax(logits),1)

    def attention(self, inputs):
        return tf.reshape(tf.matmul(tf.reshape(tf.nn.softmax(tf.reshape(tf.matmul(tf.reshape(tf.tanh(inputs), [-1, self.hidden_units]),self.attention_context),[self.batch_size, -1])),[self.batch_size,1, -1]), inputs),[self.batch_size, self.hidden_units])

def load_ckpt(model, path):
    ckpt = tf.train.Checkpoint(transformer=model, optimizer=model.opt)
    ckpt_manager = tf.train.CheckpointManager(ckpt, path, max_to_keep=5)
    # if a checkpoint exists, restore the latest checkpoint.
    if ckpt_manager.latest_checkpoint:
        ckpt.restore(ckpt_manager.latest_checkpoint)
        print ('Latest checkpoint restored!!')
    return ckpt, ckpt_manager

import pickle
from sklearn.model_selection import train_test_split                                                      
import os                                                                                                   
def readData():
  fn = 'all_data.b'
  if os.path.exists(fn):    
    print(fn)                                                                      
    train_seqs, test_seqs, train_labels, test_labels = pickle.load(open(fn,'rb'))                                              
    print(fn)
  else:                                                                                                     
    seqs, codes ,labels = utils.Lan_features(config['input'])
    print(len(labels),len(seqs))
    seqs = utils.padding_feature(seqs, config['instruction_number'], config['instruction_length'], '90')
    #pickle.dump((labels, seqs, codes),open(fn,'wb'))       
    lookupTable, labels = np.unique(np.array(labels), return_inverse=True)                                                                      
    pickle.dump(lookupTable, open('lookuptable','wb'))   
    train_seqs, test_seqs, train_labels, test_labels = train_test_split(seqs, labels, test_size=0.3)      
    pickle.dump((train_seqs, test_seqs, train_labels, test_labels), open(fn,'wb'))  
  return train_seqs, train_labels, test_seqs, test_labels 


##baseline
train_seqs, train_labels, test_seqs, test_labels = readData()
_train_seqs = np.reshape(np.array(train_seqs),(len(train_labels),-1))
_test_seqs = np.reshape(np.array(test_seqs),(len(test_labels),-1))



def test(test_img, test_lab, path):
    vt_model = VariableType()
    ckpt, ckpt_manager = load_ckpt(vt_model, path)   
    test_ds = tf.data.Dataset.from_tensor_slices((test_img, test_lab)).batch(config['batch_size'],drop_remainder=True)
    all_pred = []
    all_logits = []
    all_y = []
    for inputs, outputs in test_ds:
        logits, loss, pred = vt_model(inputs, outputs, False)
        all_pred.extend(pred.numpy())
        all_logits.extend(logits.numpy())
        all_y.extend(outputs.numpy())
    return utils.allresult(all_pred, all_y, all_logits)

def train(train_images, train_labels, test_img, test_lab, path):
    vt_model = VariableType()
    ckpt, ckpt_manager = load_ckpt(vt_model, path)
    #cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=path, save_weights_only=True, verbose=1)
    time_start = time.time()
    train_images = tf.cast(train_images, dtype=tf.float32)
    train_labels = tf.cast(train_labels, dtype=tf.float32)
    test_img = tf.cast(test_img, dtype=tf.float32)
    test_lab = tf.cast(test_lab, dtype=tf.float32)
    
    max_auc = 0
    res = []
    for epoch in range(config['max_epochs']):
        train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels)).shuffle(1000, seed=epoch*(2612)).batch(config['batch_size'],drop_remainder=True)
        for inputs, outputs in train_ds:
            logits, loss, pred = vt_model(inputs, outputs, True)
        ckpt_manager.save()
        fpr, tpr, roc_auc = test(test_img, test_lab, path)
        print('Epoch {} Loss {:.4f} Accuracy {:.4f}'.format(epoch + 1, vt_model.train_loss.result(), vt_model.train_accuracy.result()))
        if roc_auc > max_auc:
            res = (fpr, tpr, roc_auc)
    time_taken = time.time() - time_start
    print('\nTotal time taken (in seconds): {:.2f}'.format(time_taken))
    return res
    

#Lan Model
res = []
#fpr, tpr, roc_auc = train(train_seqs, train_labels, test_seqs, test_labels, config['save_path'])
fpr, tpr, roc_auc = test(test_seqs, test_labels, config['save_path'])
res.append([fpr,tpr,roc_auc,'Model1'])

# baseline
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=50,max_depth=2)
print(clf.fit(_train_seqs,train_labels).score(_test_seqs, test_labels))
fpr, tpr, roc_auc = utils.allresult(clf.predict(_test_seqs), test_labels, clf.predict_proba(_test_seqs))
res.append([fpr,tpr,roc_auc,'RF'])
pickle.dump(res, open('my_result','wb'))  
utils.savefig(res,'micro')