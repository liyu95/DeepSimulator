#!/usr/bin/env python
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

summary_dir = '../log/log_reg_seq'

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

def regression_model(train_input, test_input, model_name,
	load=False, nb_epoch=0):
	print('Setting up...May take one minute...')
	# pdb.set_trace()

	seq_train, fix_train, can_train, label_train = train_input
	seq_test, fix_test, can_test, label_test = test_input

	fix_train = np.reshape(fix_train, (-1, chunk_size, 1))
	fix_test = np.reshape(fix_test, (-1, chunk_size, 1))

	can_train = np.reshape(can_train, (-1, chunk_size, 1))
	can_test = np.reshape(can_test, (-1, chunk_size, 1))


	input_seq = tf.placeholder(tf.float32, shape=[None, n_steps, 4])
	input_seq_3 = tf.placeholder(tf.float32, shape=[None, n_steps-2, 64])
	input_seq_5 = tf.placeholder(tf.float32, shape=[None, n_steps-4, 1024])
	kr = tf.placeholder(tf.float32)
	y = tf.placeholder(tf.float32, shape=output_shape)
	phase = tf.placeholder(tf.bool, name='phase')

	pred = model_graph(input_seq, input_seq_3, input_seq_5, kr, phase)

	# learning rate decay
	global_step=tf.Variable(0,trainable=False)

	# weight decay
	loss = tf.reduce_mean(tf.losses.mean_squared_error(predictions=pred, labels=tf.reshape(y, [-1])))

	update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
	with tf.control_dependencies(update_ops):
		optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss,
			global_step=global_step)

	# for monitoring
	tf.summary.scalar('loss', loss)
	# tf.summary.scalar('accuracy', accuracy)
	merged = tf.summary.merge_all()

	sess = tf.Session(config=tf.ConfigProto(
		allow_soft_placement=True))

	# define the tensorboard writer
	if load==False:
		os.system('rm {}/train/*'.format(summary_dir))
		os.system('rm {}/test/*'.format(summary_dir))
	train_writer = tf.summary.FileWriter(summary_dir+'/train',sess.graph)
	test_writer = tf.summary.FileWriter(summary_dir+'/test')
	
	if debug_mode:
		sess = tf_debug.LocalCLIDebugWrapperSession(sess)
	init = tf.global_variables_initializer()
	sess.run(init)
	print('Graph initialized!')

	saver = tf.train.Saver()

	if load:
		saver.restore(sess, model_name)


	def model_whole_set_check(seq, fix, can, y_input, batch_size=64):
		result_pred = list()
		result_fix = list()
		result_true = list()
		seq_obj = batch_object(seq, batch_size)
		fix_obj = batch_object(fix, batch_size)
		can_obj = batch_object(can, batch_size)
		y_obj = batch_object(y_input, batch_size)
		# pdb.set_trace()
		for step in range(int(len(seq)/batch_size)):
			seq_batch = seq_obj.next_batch()
			fix_batch = fix_obj.next_batch()
			can_batch = can_obj.next_batch()
			y_batch = y_obj.next_batch()
			# y_batch = np.reshape(y_batch, [-1])
			seq_batch_3 = seq_3_encode_list(seq_batch)
			seq_batch_5 = seq_5_encode_list(seq_batch)
			temp = sess.run(pred, 
				feed_dict={input_seq: seq_batch, 
				input_seq_3: seq_batch_3, 
				input_seq_5: seq_batch_5,
				y: y_batch, kr: 1, phase: 0})
			result_fix += list(np.reshape(fix_batch,[-1]))
			result_true += list(np.reshape(y_batch,[-1]))
			result_pred += list(temp)
			if step%10==0:
				print('We are in step %d.'%step)
		# pdb.set_trace()
		print('The result of fix to true is {}'.format(mean_squared_error(result_true, 
			result_fix)))
		print('The result of pred to true is {}'.format(mean_squared_error(result_pred,
			result_true)))	
		return result_pred, result_true


	# define the training and test part
	acc_step = 0
	print('Total epoch: {}'.format(nb_epoch))
	#pdb.set_trace()
	for epoch in range(nb_epoch):
		for step in range(int(len(seq_train)/batch_size)+1):
			# seq_train_batch = seq_train_obj.next_batch()
			# fix_train_batch = fix_train_obj.next_batch()
			# can_train_batch = can_train_obj.next_batch()
			# y_train_batch = y_train_obj.next_batch()
			x_train_list, y_train_batch = generate_random_batch(
				[seq_train, fix_train, can_train], label_train, batch_size)
			# y_train_batch = np.reshape(y_train_batch, [-1])
			seq_train_1 = x_train_list[0]
			# seq_train_1 = np.reshape(seq_train_1, [-1, 104, 4, 1])
			seq_train_3 = seq_3_encode_list(x_train_list[0])
			# seq_train_3 = np.reshape(seq_train_3, [-1, 102, 64, 1])
			seq_train_5 = seq_5_encode_list(x_train_list[0])
			# seq_train_5 = np.reshape(seq_train_5, [-1, 100, 1024, 1])
			sess.run(optimizer, 
				feed_dict={input_seq: seq_train_1, 
				input_seq_3: seq_train_3, input_seq_5: seq_train_5,
				y: y_train_batch, kr: 0.7, phase: 1})
			
			if step%output_step == 0:
				summary, loss_out = sess.run([merged, loss], 
					feed_dict={input_seq: seq_train_1, 
					input_seq_3: seq_train_3, input_seq_5: seq_train_5,
					y: y_train_batch, kr: 1, phase: 0})
				train_writer.add_summary(summary, acc_step)
				# print('Train step %d'%step)
				# print('Train loss: %f, train acc: %f'%(loss_out, acc))
				print('Epoch: %d, train step %d, loss %f'%(epoch, step, loss_out))
				x_test_list, y_test_batch = generate_random_batch(
					[seq_test, fix_test, can_test], label_test, batch_size)
				# y_test_batch = np.reshape(y_test_batch, [-1])
				seq_test_1 = x_test_list[0]
				# seq_test_1 = np.reshape(seq_test_1, [-1, 104, 4, 1])
				seq_test_3 = seq_3_encode_list(x_test_list[0])
				# seq_test_3 = np.reshape(seq_test_3, [-1, 102, 64, 1])
				seq_test_5 = seq_5_encode_list(x_test_list[0])
				# seq_test_5 = np.reshape(seq_test_5, [-1, 100, 1024, 1])
				summary = sess.run(merged, feed_dict ={input_seq: seq_test_1,
					input_seq_3: seq_test_3, input_seq_5: seq_test_5,
					y: y_test_batch, kr:1,phase: 0})

				test_writer.add_summary(summary, acc_step)
				# print('Test loss: %f, test acc: %f'%(loss_out, acc))

			acc_step = acc_step+1

		saver.save(sess, model_name)
	
	result_pred, result_true = model_whole_set_check(seq_test, fix_test, can_test,
		label_test, 256)

	return result_pred, result_true
