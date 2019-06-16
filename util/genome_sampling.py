#!/usr/bin/env python

import argparse
import numpy as np
import scipy.stats as st
import random
# s18
# beta distribution with parameters
# 1.7780912583853339, 
# 7.8927794827841975, 
# 316.75817723758286, 
# 34191.25716704056
def draw_beta_dis(size, mean, seed):
	samples = st.beta.rvs(1.778, 7.892, 316.758, 
		34191.257, size=size, random_state=seed)
	samples = samples*mean/6615.0
	samples = samples.astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples

# human
# alpha distribution with parameters
# 0.0058193182047962533, 
# -49.180482198937398, 
# 1663.9103931473874
def draw_alpha_dis(size, mean, seed):
	samples = st.alpha.rvs(0.00582,-49.1805,1663.91,
		size=size, random_state=seed)
	samples = samples*mean/7106.0
	samples = samples.astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples


def draw_expon_dis(size, mean, seed):
	samples = st.expon.rvs(213.98910256668592, 
		6972.5319847131141, size=size, random_state=seed)
	samples = samples*mean/7106.0
	samples = samples.astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples

# lambda
# the actual length should be multiplied  by 1000
# two mixture gamma distribution with parameters
# first gamma: alpha: 6.3693711, rate: 0.53834893
# second gamma: alpha: 1.67638771, rate: 0.22871401
def draw_mix_gamma_dis(size, mean, seed):
	half = int(size/2.0)
	sample_1 = st.gamma.rvs(6.3693711, 0.53834893, size=half,
		random_state=seed)
	sample = st.gamma.rvs(1.67638771, 0.22871401, size=(size-half),
		random_state=seed)
	sample = np.concatenate((sample, sample_1))
	np.random.seed(seed)
	np.random.shuffle(sample)
	sample = sample*mean/4.39
	sample = sample.astype(int)
	sample = np.clip(sample, 1, len(genome))
	return sample

def load_genome(input_file):
	with open(input_file, 'r') as f:
		text = f.read()
		lines = text.splitlines()
	sequence = filter(lambda x: '>' not in x, lines)
	sequence = map(lambda x: x.strip(), sequence)
	sequence = ''.join(sequence)
	return sequence

def sampling_single_cir(pair):
	start_point, read_length = pair
	if len(genome)>=(start_point+read_length):
		return genome[start_point: start_point+read_length]
	else:
		return genome[start_point:]+genome[:start_point+read_length-len(genome)]

def get_start_point(length):
	return np.random.choice(len(genome)-length+1, 1)[0]

def sampling_single_lin(pair):
	start_point, read_length = pair
	return genome[start_point: start_point+read_length]

def sampling(read_length, circular, seed):
	np.random.seed(seed)
	read_list = list()
	if circular:
		start_point = np.random.choice(len(genome), len(read_length),
			replace=True)
		chunk_pair = zip(start_point, read_length)
		read_list = map(sampling_single_cir, chunk_pair)
	else:
		start_point = map(get_start_point, read_length)
		chunk_pair = zip(start_point, read_length)
		read_list = map(sampling_single_lin, chunk_pair)
	return read_list

def save_file(read_list, output_file):
	with open(output_file, 'w') as f:
		for i in range(len(read_list)):
			f.write('>{}\n'.format(i))
			f.write(read_list[i]+'\n')


def check_mean_length(file_path):
	with open(file_path, 'r') as f:
		a = f.read()
		l = a.splitlines()
	l = list(filter(lambda x: '>' not in x, l))
	length = list(map(len, l))
	print('The average length is: ', np.average(length))	

# --------------- main ------------------#
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='sampling read from the \
		input genome')
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input genome file in fasta format')
	parser.add_argument('-p', action='store', dest='output', required=True,
		help='prefix the output file')
	parser.add_argument('-n', action='store', dest='seq_num', required=True,
		type=int, help='the number of output sequence')
	parser.add_argument('-l', action='store', dest='len_mean',default=8000, 
		type=float, help='the rough mean of the read length')
	parser.add_argument('-S', action='store', dest='seed', type=int, default=0,
		help='the random seed, for reproducibility')
	parser.add_argument('-K', action='store', dest='coverage', type=int, default=0,
		help='spacify the simulation coverage, the nubmer of read will be \
		calculated. We use the larger one compared with seq_num.')
	parser.add_argument('-d', action='store', dest='dis', default=3,
		type=int, help='choose from the following distribution: \
		1: beta_distribution, 2: alpha_distribution, 3: mixed_gamma_dis \
		default: 3. If the read length drawn from the distribution is \
		larger than the length of the genome, the value is clipped to the\
		length of the genome')
	parser.add_argument('-c', action='store', dest='circular',
		default=False, type=bool, help='if the genome is circular')

	arg = parser.parse_args()
	random.seed(arg.seed)
	genome = load_genome(arg.input)
	seq_num_c = int(arg.coverage*len(genome)/4400)
	seq_num = arg.seq_num
	if seq_num_c>seq_num:
		seq_num = seq_num_c

	if arg.dis == 3:
		read_length = draw_mix_gamma_dis(seq_num, arg.len_mean, arg.seed)
	elif arg.dis == 2:
		read_length = draw_expon_dis(seq_num, arg.len_mean, arg.seed)
	elif arg.dis == 1:
		read_length = draw_beta_dis(seq_num, arg.len_mean, arg.seed)
	elif arg.dis == 0:
		print('This is for testing only')
		read_length = np.random.normal(5, 1, seq_num)
		read_length = read_length.astype(int)
	else:
		print('Invalid distribution, we would use mixed gamma distribution')
		read_length = draw_mix_gamma_dis(seq_num, arg.len_mean, arg.seed)
	print('The average length is: ', np.average(read_length))
	read_list = sampling(read_length, arg.circular, arg.seed)
	save_file(read_list, arg.output+'.fasta')
