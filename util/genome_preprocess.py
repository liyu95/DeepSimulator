#!/usr/bin/env python

import argparse
import numpy as np
import re


#------------- functions ---------------#
def load_genome(input_file):
	with open(input_file, 'r') as f:
		text = f.read()
		lines = text.splitlines()
	sequence = filter(lambda x: '>' not in x, lines)
	sequence = map(lambda x: x.strip(), sequence)
	sequence = ''.join(sequence)
	return sequence

def save_genome(genome, output_file):
	with open(output_file, 'w') as f:
		f.write('>preprocess\n')
		f.write(genome+'\n')

def replace_n(genome):
	n_index = [m.start() for m in re.finditer('N', genome)]
	genome_list = np.array([x for x in genome])
	random_base = np.random.choice(['A','T','C','G'],len(n_index))
	genome_list[n_index] = random_base
	genome = ''.join(genome_list)
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

	arg = parser.parse_args()
	genome = load_genome(arg.input)

	# deal with the not standard genome, containing 'N', or in lower case.
	genome = genome.upper()
	# replace all non ATCG nucleotides into 'N'
	genome = re.sub('[^ATCG]', 'N', genome)

	if arg.replace:
		genome = replace_n(genome)
	else:
		genome = genome.replace('N','')

	# output genome
	save_genome(genome, arg.output)
