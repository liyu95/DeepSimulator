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
TEMPLATE_FILE=template.fast5
home=`pwd`

#----- get input name ---#
fulnam=`basename $FULLFILE`
relnam=${fulnam%.*}

#----- create tmp_dir ---#
DATE=`date '+%Y_%m_%d_%H_%M_%S'`
tmp_root="/tmp/PORE_MODEL_${relnam}_${RANDOM}_${DATE}"
mkdir -p $tmp_root

#------ choose different pore model ----#
if [ $CONTEXT -eq 0 ]
then
	#-> context-dependent pore model
	source activate tensorflow_cdpm
	export DeepSimulatorHome=$home
	python2 $home/pore_model/src/context_simulator.py \
		-i $FULLFILE -p $PREFIX -l $PREFIX -t $THREAD_NUM \
		-F $tmp_root -T $home/util/$TEMPLATE_FILE \
		--perfect True --sigout True
	source deactivate
else
	#-> official kmer pore model
	source activate tensorflow_cdpm
	python2 $home/pore_model/src/kmer_simulator.py \
		-i $FULLFILE -p $PREFIX -l $PREFIX -t $THREAD_NUM \
		-F $tmp_root -T $home/util/$TEMPLATE_FILE \
		-m $home/pore_model/model/$MODEL_FILE \
		--perfect True --sigout True
	source deactivate
fi


#---- remove tmp_dir ---#
rm -rf $tmp_root

