import numpy as np
from multiprocessing import Pool
import pdb

# the threshold for creat bins
threshold = 2.5
# num_bins = 100 + 2
num_bins = 25 + 2
bin_size = threshold*2/(num_bins-2)

data_type =['sequence', 'fix_value', 'can_value', 'label','adp']

# use this in case, otherwise use digitize
def discretization(value, threshold, num_bins, bin_size):
	if value <= -threshold:
		return 0
	if value > threshold:
		return num_bins-1
	return math.ceil((value+threshold)/bin_size)

def get_value(file, column_ind=3):
	with open(file, 'r') as f:
		text = f.read()
		line_list = text.splitlines()
	line_list = line_list[2:]
	value = map(lambda x: x.split()[column_ind], line_list)
	value = np.array(value).astype(float)
	return value

def get_adp_value(file):
	return get_value(file, 9)

def get_fix_value(file):
	return get_value(file, 4)

def get_can_value(file):
	return get_value(file, 3)

def get_5_mer_code(file):
	return get_value(file, 1)

def get_sequence(file):
	with open(file, 'r') as f:
		text = f.read()
		line_list = text.splitlines()
	return line_list[1]

def get_rev_for_code(dataset):
	with open('../data/{}_list.data_reso'.format(dataset), 'r') as f:
		text = f.read()
		line_list = text.splitlines()
	data_list = map(lambda x: x.split()[1], line_list)
	data = np.array(data_list).astype(float)
	return data

def get_data_list(dataset):
	with open('../data/{}_list.data_reso'.format(dataset), 'r') as f:
		text = f.read()
		line_list = text.splitlines()
	data_list = map(lambda x: x.split()[0], line_list)
	return data_list

def get_value_all_dataset(dataset):
	with open('../data/train_file.list', 'r') as f:
		text = f.read()
		line_list = text.splitlines()
	data_list = map(lambda x: x.split('/')[-1], line_list)
	datafold = '../data/inter_data/'
	file_list = map(lambda x: datafold + x +'.data', data_list)
	# pdb.set_trace()
	p = Pool()
	adp_value = p.map(get_adp_value, file_list)
	fix_value = p.map(get_fix_value, file_list)
	label = p.map(get_5_mer_code, file_list)
	sequence_list = p.map(get_sequence, file_list)
	can_value = p.map(get_can_value, file_list)
	return sequence_list, label, adp_value, fix_value, can_value



def digitization(array):
	bins = np.linspace(-threshold, threshold, num_bins-1,
		endpoint=True)
	ind = np.digitize(array, bins)
	return ind
	

def build_dictionary(key_list, value_list):
	d = dict()
	for i in range(len(key_list)):
		d[key_list[i]] = value_list[i]
	return d

def rev_for_sep(l, code_list):
	array = np.array(l)
	code_array = np.array(code_list)
	for_list = list(array[np.where(code_array==0)])
	rev_list = list(array[np.where(code_array==1)])
	return for_list, rev_list

def value_to_label(value_list):
	p = Pool()
	label_list = p.map(digitization, value_list)
	return label_list

def generate_chunk(inputs, chunk_size=100, stride=100):
	sequence, fix_value, can_value, label, adp = inputs
	num_full_chunk = int(float(len(label)-chunk_size)/stride)+1
	label_list = list()
	value_list = list()
	can_list = list()
	sequence_list = list()
	adp_list = list()
	for i in range(num_full_chunk):
		label_list.append(label[i*stride:i*stride+chunk_size])
		value_list.append(fix_value[i*stride:i*stride+chunk_size])
		can_list.append(can_value[i*stride:i*stride+chunk_size])
		sequence_list.append(sequence[i*stride:i*stride+chunk_size+4])
		adp_list.append(adp[i*stride:i*stride+chunk_size])
	return (np.array(sequence_list), np.array(value_list), 
		np.array(can_list), np.array(label_list),np.array(adp_list))

def convert_to_chunk(sequence_list, fix_value_list, can_value_list, label_list,
	adp_list):
	p = Pool()
	input_list = zip(sequence_list, fix_value_list, can_value_list, label_list,
		adp_list)
	output_list = p.map(generate_chunk, input_list)
	p.close()
	sequence_chunk, value_chunk, can_chunk, label_chunk, adp_chunk = zip(*output_list)
	# pdb.set_trace()
	sequence_chunk = np.vstack(sequence_chunk)
	value_chunk = np.vstack(value_chunk)
	can_chunk = np.vstack(can_chunk)
	label_chunk = np.vstack(label_chunk)
	adp_chunk =  np.vstack(adp_chunk)
	return sequence_chunk, value_chunk, can_chunk, label_chunk, adp_chunk


def sequence_encoding(sequence):
	encoding_dict = {'A': np.array([1.0,0.0,0.0,0.0]),
					'T': np.array([0.0,1.0,0.0,0.0]),
					'C': np.array([0.0,0.0,1.0,0.0]),
					'G': np.array([0.0,0.0,0.0,1.0])}
	encoding_list = map(lambda x: encoding_dict[x], sequence)
	encoding = np.array(encoding_list)
	return encoding

def encoding_all(sequence_list):
	p = Pool()
	encoding = p.map(sequence_encoding, sequence_list)
	return np.array(encoding)

def get_dataset_data(dataset):
	sequence_list, mer_list, adp_value, fix_value, can_value = get_value_all_dataset(
		dataset)
	sequence_list_for=sequence_list
	encoding_for = encoding_all(sequence_list_for)

	adp_value_for = adp_value
	label_for = value_to_label(adp_value_for)

	fix_value_for = fix_value
	can_value_for = can_value

	# pdb.set_trace()
	sequence_chunk_for, value_chunk_for, can_chunk_for, label_chunk_for, adp_chunk_for = convert_to_chunk(
		encoding_for, fix_value_for, can_value_for, label_for, adp_value_for)

	for_dict = build_dictionary(data_type, [sequence_chunk_for, value_chunk_for,
		can_chunk_for, label_chunk_for, adp_chunk_for])

	return for_dict

if __name__ == '__main__':
	pass