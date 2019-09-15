#!/usr/bin/env python
import argparse
from Bio import SeqIO
import os

def load_fasta(input_file):
	id_list = list()
	sequence_list = list()
	for record in SeqIO.parse(input_file, "fasta"):
		id_list.append(record.id)
		sequence_list.append(record.seq)
	fasta_list = zip(id_list, sequence_list)
	return list(fasta_list)

def write_fasta(prefix, fasta_list):
	if not os.path.exists(prefix):
		os.makedirs(prefix)
	for i in range(len(fasta_list)):
		with open(os.path.join(prefix, 'contig_{}.fasta'.format(i)), 'w') as f:
			fasta_id = '>'+fasta_list[i][0]
			fasta_seq = str(fasta_list[i][1])
			f.write(fasta_id+'\n'+fasta_seq)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='sampling read from the \
		input genome')
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input fasta file with multiple contigs')
	parser.add_argument('-p', action='store', dest='output', required=True,
		help='the output folder')
	arg = parser.parse_args()
	fasta_list = load_fasta(arg.input)
	write_fasta(arg.output, fasta_list)
