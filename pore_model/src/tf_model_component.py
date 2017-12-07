#!/usr/bin/env python

import numpy as np
from numpy.random import randint
import tflearn
import tensorflow as tf
from tensorflow.python.framework import ops

def selu(x):
    with ops.name_scope('elu') as scope:
        alpha = 1.6732632423543772848170429916717
        scale = 1.0507009873554804934193349852946
        return scale*tf.where(x>=0.0, x, alpha*tf.nn.elu(x))

#functions to generate variables, like weight and bias
def weight_variable(shape):
    import math
    if len(shape)>2:
        weight_std=math.sqrt(2.0/(shape[0]*shape[1]*shape[2]))
    else:
        weight_std=math.sqrt(2.0/shape[0])
    initial=tf.truncated_normal(shape,stddev=weight_std)
    return tf.Variable(initial,name='weights')

def bias_variable(shape):
    initial=tf.constant(0.1,shape=shape)
    return tf.Variable(initial,name='bias')

def conv1d(x, W):
	return tf.nn.conv1d(x, W, stride=1, padding='SAME')

def conv2d(x,W):
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')

def aver_pool2d(x,row,col):
    #Be careful about the dimensionality reduction of pooling and strides setting
    return tf.nn.avg_pool(x,ksize=[1,row,col,1],strides=[1,row,col,1],padding='SAME')

def max_pool2d(x,row,col):
    return tf.nn.max_pool(x,ksize=[1,row,col,1],strides=[1,row,col,1],padding='SAME')


def batch_process(feature, batch_index):
    feature_batch = []
    for index in batch_index:
        feature_batch.append(feature[index])
    feature_batch = np.array(feature_batch)
    feature_batch = feature_batch.astype('float')
    return feature_batch

def generate_random_batch(feature_list, label, batch_size):
    batch_index = randint(0,len(label),batch_size)
    feature_batch_list = map(lambda x: batch_process(x, batch_index),
    	feature_list)
    label_batch = batch_process(label, batch_index)
    return (feature_batch_list, label_batch)

# map the label to continuous start from 0
def label_remapping(label_list):
	unique_label=list(set(label_list))
	unique_label.sort()
	label_mapping_dict={}
	for i in range(len(unique_label)):
	    label_mapping_dict[unique_label[i]]=i
	label_list_temp=[]
	for i in range(len(label_list)):
	    label_list_temp.append(label_mapping_dict[label_list[i]])
	return label_list_temp

def label_one_hot(label_array):
	from sklearn.preprocessing import OneHotEncoder
	enc=OneHotEncoder()
	label_list=[]
	for i in range(len(label_array)):
		label_list.append([label_array[i]])
	return enc.fit_transform(label_list).toarray()

# n_layers: number of layers,
# hidden_nodes: a list to indicate the number of nodes in each layers
def fully_connected(n_layers, hidden_nodes, input):
	input_len = input.get_shape().as_list()[-1]
	input = tflearn.batch_normalization(input)
	with tf.name_scope('fc_layer_1'):
		w_fc1 = weight_variable([input_len,hidden_nodes[0]])
		b_fc1 = bias_variable([hidden_nodes[0]])
		output = tf.nn.relu(tf.matmul(input,w_fc1)+b_fc1)
		output = tflearn.batch_normalization(output)
	for i in xrange(1, n_layers):
		with tf.name_scope('fc_layer_'+str(i+1)):
			w = weight_variable([hidden_nodes[i-1], hidden_nodes[i]])
			b = bias_variable([hidden_nodes[i]])
			output = tf.nn.relu(tf.matmul(output,w)+b)
			output = tflearn.batch_normalization(output)

	return output


