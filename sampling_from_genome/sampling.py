#!/usr/bin/env python

import argparse
import numpy as np
import scipy.stats as st
import re
import random
# s18
# beta distribution with parameters
# 1.7780912583853339, 
# 7.8927794827841975, 
# 316.75817723758286, 
# 34191.25716704056
def draw_beta_dis(size):
	samples = st.beta.rvs(1.778, 7.892, 316.758, 
		34191.257, size=size)
	samples = samples.astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples

# human
# alpha distribution with parameters
# 0.0058193182047962533, 
# -49.180482198937398, 
# 1663.9103931473874
def draw_alpha_dis(size):
	samples = st.alpha.rvs(0.00582,-49.1805,1663.91,
		size=size).astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples


def draw_expon_dis(size):
	samples = st.expon.rvs(213.98910256668592, 
		6972.5319847131141, size=size).astype(int)
	samples = np.clip(samples, 1, len(genome))
	return samples

# lambda
# the actual length should be multiplied  by 1000
# two mixture gamma distribution with parameters
# first gamma: alpha: 6.3693711, rate: 0.53834893
# second gamma: alpha: 1.67638771, rate: 0.22871401
def draw_mix_gamma_dis(size):
	half = int(size/2.0)
	sample_1 = st.gamma.rvs(6.3693711, 0.53834893, size=half)
	sample = st.gamma.rvs(1.67638771, 0.22871401, size=(size-half))
	sample = np.concatenate((sample, sample_1))
	np.random.shuffle(sample)
	sample = sample*1000
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

def sampling(read_length, circular):
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

def replace_n(genome):
	n_index = [m.start() for m in re.finditer('N', genome)]
	genome_list = np.array([x for x in genome])
	random_base = np.random.choice(['A','T','C','G'],len(n_index))
	genome_list[n_index] = random_base
	genome = ''.join(genome_list)
	return genome
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='sampling read from the \
		input genome')
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input genome file in fasta format')
	parser.add_argument('-p', action='store', dest='output', required=True,
		help='prefix the output file')
	parser.add_argument('-n', action='store', dest='seq_num', required=True,
		type=int, help='the number of output sequence')
	parser.add_argument('-d', action='store', dest='dis', default=3,
		type=int, help='choose from the following distribution: \
		1: beta_distribution, 2: alpha_distribution, 3: mixed_gamma_dis \
		default: 3. If the read length drawn from the distribution is \
		larger than the length of the genome, the value is clipped to the\
		length of the genome')
	parser.add_argument('-c', action='store', dest='circular',
		default=False, type=bool, help='if the genome is circular')

	parser.add_argument('-r', action='store', dest='replace',
		default=False, type=bool, help='if we replace the ns or delete the ns')

	arg = parser.parse_args()
	genome = load_genome(arg.input)

	# deal with the not standard genome, containing 'N', or in lower case.
	genome = genome.upper()

	if arg.replace:
		genome = replace_n(genome)
	else:
		genome = genome.replace('N','')

	with open(arg.input+'.preprocessed', 'w') as f:
		f.write(genome)

	if arg.dis == 3:
		read_length = draw_mix_gamma_dis(arg.seq_num)
	elif arg.dis == 2:
		read_length = draw_expon_dis(arg.seq_num)
	elif arg.dis == 1:
		read_length = draw_beta_dis(arg.seq_num)
	elif arg.dis == 0:
		print('This is for testing only')
		read_length = np.random.normal(5, 1, arg.seq_num)
		read_length = read_length.astype(int)
	else:
		print('Invalid distribution, we would use mixed gamma distribution')
		read_length = draw_mix_gamma_dis(arg.seq_num)
	read_list = sampling(read_length, arg.circular)
	save_file(read_list, arg.output+'.fasta')