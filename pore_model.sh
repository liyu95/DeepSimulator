#!/bin/bash

if [ $# -lt 2 ]
then
	echo "Usage: ./pore_model.sh <input_genomic_sequence> <context_or_kmer> "
	echo "[note]: context_or_kmer: 0 for context-dependent pore_model "
	echo "                         1 for kmer official pore_model "
	exit
fi


#------ read input arguments ---------#
FULLFILE=$1
CONTEXT=$2
PREFIX=signal
THREAD_NUM=1
MODEL_FILE=template_median68pA.model
home=`pwd`


#------ choose different pore model ----#
if [ $CONTEXT -eq 0 ]
then
	#-> context-dependent pore model
	source activate tensorflow_cdpm
	export DeepSimulatorHome=$home
	python2 $home/pore_model/src/context_simulator.py \
		-i $FULLFILE -p $PREFIX -l $PREFIX -t $THREAD_NUM \
		--perfect True
	source deactivate
else
	#-> official kmer pore model
	source activate tensorflow_cdpm
	python2 $home/pore_model/src/kmer_simulator.py \
		-i $FULLFILE -p $PREFIX -l $PREFIX -t $THREAD_NUM \
		-m $home/pore_model/model/$MODEL_FILE \
		--perfect True
	source deactivate
fi

