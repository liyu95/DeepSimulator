#!/usr/bin/env python

import argparse
import numpy as np
import re
import random
from Bio import SeqIO


#------------- functions ---------------#
# def load_genome(input_file):
# 	with open(input_file, 'r') as f:
# 		text = f.read()
# 		lines = text.splitlines()
# 	sequence = filter(lambda x: '>' not in x, lines)
# 	headers = filter(lambda x: '>' in x, lines)
# 	sequence = map(lambda x: x.strip(), sequence)
# 	sequence = filter(len, sequence)
# 	seq_lens = map(len, sequence)
# 	sequence = ''.join(sequence)
# 	return sequence, headers, seq_lens

def load_genome(input_file):
	id_list = list()
	sequence_list = list()
	for record in SeqIO.parse(input_file, "fasta"):
		id_list.append(record.id)
		sequence_list.append(record.seq)

	sequence = list(map(str, sequence_list))
	with open(input_file, 'r') as f:
		text = f.read()
		lines = text.splitlines()
	headers = filter(lambda x: '>' in x, lines)
	seq_lens = list(map(len, sequence))
	sequence = ''.join(sequence)
	return sequence, headers, seq_lens

def save_genome(genome, output_file, headers, seq_lens, multi=False):
	# print(seq_lens)
	if multi:
		seq_lens = [0]+seq_lens
		for i in range(len(headers)):
			with open(output_file+'_{}'.format(i), 'w') as f:
				f.write(headers[i]+'\n')
				sequence = genome[sum(seq_lens[:i+1]):sum(seq_lens[:i+2])]
				# print(sum(seq_lens[:i+1]))
				# print(sum(seq_lens[:i+2]))
				f.write(sequence+'\n')

	else:
		with open(output_file, 'w') as f:
			f.write('>preprocess\n')
			f.write(genome+'\n')

# def replace_n(genome):
# 	n_index = [m.start() for m in re.finditer('N', genome)]
# 	genome_list = np.array([x for x in genome])
# 	random_base = np.random.choice(['A','T','C','G'],len(n_index))
# 	genome_list[n_index] = random_base
# 	genome = ''.join(genome_list)
# 	return genome

def callback(matchobj):
	return random.choice(['A','T','C','G'])

def replace_n(genome):
	genome = re.sub(r'N', callback, genome)
	return genome

#============== main =====================#
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='pre-process input genome')

	#-> required arguments
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input genome file in fasta format')
	parser.add_argument('-o', action='store', dest='output', required=True,
		help='prefix the output file')
	#-> optional arguments
	parser.add_argument('-r', action='store', dest='replace',
		default=False, type=bool, help='set if we replace the \'N\'s (default: delete the \'N\'s)')
	parser.add_argument('-m', action='store', dest='multi',
		default=False, type=bool, help='set to indicate the input contains multiple contigs (default: False')

	arg = parser.parse_args()
	genome, headers, seq_lens = load_genome(arg.input)

	# deal with the not standard genome, containing 'N', or in lower case.
	genome = genome.upper()
	# replace all non ATCG nucleotides into 'N'
	genome = re.sub('[^ATCG]', 'N', genome)

	if arg.replace:
		genome = replace_n(genome)
	else:
		genome = genome.replace('N','')

	# output genome
	save_genome(genome, arg.output, headers, seq_lens, multi=arg.multi)
