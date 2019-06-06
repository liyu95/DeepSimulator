from data_pre import *
import math
import numpy as np
from multiprocessing import Pool
# from conv_regression import regression_model
from model_graph import *
import cPickle
import gc
import os

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# the threshold for creat bins
threshold = 2.5
# num_bins = 100 + 2
num_bins = 25 + 2
bin_size = threshold*2/(num_bins-2)

data_type =['sequence', 'fix_value', 'can_value', 'label','adp']


def write_100_lines(f, l1,l2,l3):
	for i in range(len(l1)):
		f.write('\t'.join([str(l1[i]), str(l2[i]), str(l3[i])])+'\n')


def write_result(result_true, result_pred, dataset, order,model_name):
	print('Start load data')
	data_list = get_data_list(dataset)
	sequence_list, _, adp_value, _, _ = get_value_all_dataset(
		dataset)
	rev_pro_cod = get_rev_for_code(dataset)
	sequence_list_for, sequence_list_rev = rev_for_sep(sequence_list,
		rev_pro_cod)
	adp_value_for, adp_value_rev = rev_for_sep(adp_value,
		rev_pro_cod)
	name_list_for, name_list_rev = rev_for_sep(data_list, rev_pro_cod)

	print('Finish load data')

	if order =='rev':
		sequence_list=sequence_list_rev
		name_list = name_list_rev
		label_list = adp_value_rev
		del name_list_for
		del sequence_list_for
		del adp_value_for
		gc.collect()

	if order == 'for':
		sequence_list = sequence_list_for
		name_list = name_list_for
		label_list = adp_value_for
		del name_list_rev
		del sequence_list_rev
		del adp_value_rev
		gc.collect()

	pdb.set_trace()
	acc_flag = 0
	for i in range(len(name_list)):
		if i%100==0:
			print i
		with open('../result/{}_{}_from_{}/{}'.format(dataset,order,
			model_name, name_list[i]), 'w') as f:
			n_chunk = len(label_list[i])/100
			temp_seq = sequence_list[i]
			for j in range(n_chunk):
				write_100_lines(f, temp_seq[j*100:(j+1)*100],
					result_true[(acc_flag+j)*100:(acc_flag+j+1)*100],
					result_pred[(acc_flag+j)*100:(acc_flag+j+1)*100])
			acc_flag += n_chunk

if __name__ == '__main__':
	print('Getting the customized data')
	for_dict = get_dataset_data('customized')
	print('Finishing getting the customized data')

	train_input = (for_dict['sequence'], for_dict['fix_value'],
		for_dict['can_value'], for_dict['adp'])
	test_input = (for_dict['sequence'], for_dict['fix_value'],
		for_dict['can_value'], for_dict['adp'])

	print('Model training start!!')
	result_pred, result_true = regression_model(train_input, test_input, 
		'../model/model_customized.ckpt',
		False, 10000)
	print('Model training finished!!')
