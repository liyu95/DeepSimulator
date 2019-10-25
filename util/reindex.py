#!/usr/bin/env python

import argparse
import numpy as np
import re


#------------- functions ---------------#
def load_genome(input_file):
	with open(input_file, 'r') as f:
		text = f.read()
		lines = text.splitlines()
	sequence = list(filter(lambda x: '>' not in x, lines))
	sequence = list(map(lambda x: x.strip(), sequence))
	sequence = list(filter(len, sequence))
	return sequence

def save_genome(genomes, output_file):
	with open(output_file, 'w') as f:
		for i in range(len(genomes)):
			f.write('>{}\n'.format(i))
			f.write(genomes[i]+'\n')

#============== main =====================#
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='reindex the sampled reads')

	#-> required arguments
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input genome file in fasta format')

	arg = parser.parse_args()
	genomes = load_genome(arg.input)
	# output genome
	save_genome(genomes, arg.input)
