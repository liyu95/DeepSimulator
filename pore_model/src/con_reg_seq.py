from __future__ import print_function

import tensorflow as tf
from tensorflow.contrib import rnn
from batch_object import *
from tf_model_component import *
# import tflearn
from evaluate_model import evaluate_model
import numpy as np
import pdb
from tensorflow.python import debug as tf_debug
from sklearn.metrics import mean_squared_error
import os
import math
from multiprocessing import Pool

n_class = 1

n_steps = 104
chunk_size = 100

input_value_shape = [None, chunk_size, 1]
output_shape = [None, 100]
learning_rate = 1e-4
weight_decay = 1e-4
batch_size = 64
output_step = 100
n_hidden = 25*4
debug_mode = False

summary_dir = os.environ['DeepSimulatorHome'] + '/pore_model/log/log_reg_seq'
model_dir = os.environ['DeepSimulatorHome'] + '/pore_model/model/model_reg_seqs_gn179.ckpt'


def check_mkdir(summary_dir):
	if not os.path.isdir(summary_dir):
		os.system('mkdir '+summary_dir)


weights = {
	'out': weight_variable([2*n_hidden, n_class])
}

biases = {
	'out': bias_variable([n_class])
}

# input is a batch of one d sequence
# output should be a flatten two d matrix, originally it should
# be 3d, but we flat out batch. we would like to make sure the out
# channel is n_hidden

def model_graph(seq_1, seq_3, seq_5, keep_ratio, phase):
	# pdb.set_trace()
	with tf.device('/gpu:1'):
		with tf.name_scope('sequence_1'):
			lstm_fw_cell_1 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			lstm_bw_cell_1 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			seq_1_x = tf.unstack(seq_1, 104, 1)
			seq_1_out,_,_ = rnn.static_bidirectional_rnn(lstm_fw_cell_1, 
				lstm_bw_cell_1,seq_1_x, dtype=tf.float32, scope='seq_1')
			seq_1_cut = seq_1_out[2:-2]
			seq_1_temp = tf.transpose(seq_1_cut, [1, 0, 2])
			seq_1_reshape = tf.reshape(seq_1_temp, [-1, 1*n_hidden])

		#pdb.set_trace()
		with tf.name_scope('sequence_3'):
			lstm_fw_cell_3 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			lstm_bw_cell_3 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			seq_3_x = tf.unstack(seq_3, 102, 1)
			seq_3_out,_,_ = rnn.static_bidirectional_rnn(lstm_fw_cell_3, 
				lstm_bw_cell_3,seq_3_x, dtype=tf.float32, scope='seq_3')
			seq_3_cut = seq_3_out[1:-1]
			seq_3_temp = tf.transpose(seq_3_cut, [1, 0, 2])
			seq_3_reshape = tf.reshape(seq_3_temp, [-1, 1*n_hidden])


	with tf.device('/gpu:0'):
		with tf.name_scope('sequence_5'):
			lstm_fw_cell_5 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			lstm_bw_cell_5 = rnn.BasicLSTMCell(n_hidden/2, forget_bias=1.0)
			seq_5_x = tf.unstack(seq_5, 100, 1)
			seq_5_out,_,_ = rnn.static_bidirectional_rnn(lstm_fw_cell_5, 
				lstm_bw_cell_5,seq_5_x, dtype=tf.float32, scope='seq_5')
			seq_5_temp = tf.transpose(seq_5_out, [1, 0, 2])
			seq_5_reshape = tf.reshape(seq_5_temp, [-1, 1*n_hidden])

	with tf.name_scope('reshape_concat'):
		seq_all = tf.concat([seq_1_reshape, seq_3_reshape, seq_5_reshape], 1)

	with tf.name_scope('fc1'):
		weight_fc1 = weight_variable([3*n_hidden,2*n_hidden])
		b_fc1 = bias_variable([2*n_hidden])
		f_fc1 = tf.matmul(seq_all, weight_fc1) + b_fc1

		f_fc1_bn = tf.contrib.layers.batch_norm(f_fc1, center=True, 
			scale=True, is_training=phase)

		f_fc1_out = tf.nn.relu(f_fc1_bn)

	# output_drop = tf.nn.dropout(f_fc1_out, keep_ratio)
	out = tf.matmul(f_fc1_out, weights['out']) + biases['out']
	out = tf.reshape(out, [-1])
	return out

def seq_further_encoding_3(seq):
	seq = np.argmax(seq, 1)
	start_index = 1
	size_per_loc = math.pow(4, 3)
	encoding = np.zeros([len(seq)-2,int(size_per_loc)])
	for i in range(1, len(seq)-1):
		index_temp = seq[i-1]*math.pow(4,2) + seq[i]*4 + seq[i+1]
		encoding[i-start_index, int(index_temp)] = 1
	return encoding

def seq_3_encode_list(seq_list):
	# p = Pool()
	encoding_list = map(seq_further_encoding_3, seq_list)
	return encoding_list

def seq_further_encoding_5(seq):
	seq = np.argmax(seq, 1)
	start_index = 2
	size_per_loc = math.pow(4, 5)
	encoding = np.zeros([len(seq)-4,int(size_per_loc)])
	for i in range(2, len(seq)-2):
		index_temp = seq[i-2]*math.pow(4,4) + seq[i-1]*math.pow(4,3) + \
			seq[i]*math.pow(4,2) + seq[i+1]*math.pow(4,1) + seq[i+2]
		encoding[i-start_index, int(index_temp)] = 1
	return encoding

def seq_5_encode_list(seq_list):
	# p = Pool()
	encoding_list = map(seq_further_encoding_5, seq_list)
	return encoding_list



input_seq = tf.placeholder(tf.float32, shape=[None, n_steps, 4])
input_seq_3 = tf.placeholder(tf.float32, shape=[None, n_steps-2, 64])
input_seq_5 = tf.placeholder(tf.float32, shape=[None, n_steps-4, 1024])
kr = tf.placeholder(tf.float32)
phase = tf.placeholder(tf.bool, name='phase')

pred = model_graph(input_seq, input_seq_3, input_seq_5, kr, phase)


def model_whole_set_check(seq, batch_size=64):
	sess = tf.Session(config=tf.ConfigProto(
		allow_soft_placement=True,
		intra_op_parallelism_threads=1,
		inter_op_parallelism_threads=1))
	sess.run(tf.global_variables_initializer())
	saver = tf.train.Saver()
	saver.restore(sess, model_dir)
	#print((str)(model_dir))
	#print('Model loaded!')
	result_pred = list()
	seq_obj = batch_object(seq, batch_size)
	for step in range(int(len(seq)/batch_size)+1):
		# pdb.set_trace()
		seq_batch = seq_obj.next_batch()
		seq_batch_3 = seq_3_encode_list(seq_batch)
		seq_batch_5 = seq_5_encode_list(seq_batch)
		temp = sess.run(pred, 
			feed_dict={input_seq: seq_batch, 
			input_seq_3: seq_batch_3, 
			input_seq_5: seq_batch_5,
			kr: 1, phase: 0})
		result_pred += list(temp)
	sess.close()
	return result_pred

