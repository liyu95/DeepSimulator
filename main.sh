#!/bin/bash

# processing the input parameter
while [[ -n $1 ]]; do
        # echo "\$1=$1"
        case $1 in
                -f | --filename )       shift
                                                FULLFILE=$1
                                                ;;                      
        esac
        shift
done
FILE_N=$(basename "$FULLFILE")
EXTENSION="${FILE_N##*.}"
# use the filename to name the tmp files
FILENAME="${FILE_N%.*}"

NUM=$(fgrep -o '>' $FULLFILE | wc -l)
PREFIX="signal"

# the input should be a fasta file
# we should make a tmp directory named after the input file to
# store the tmp files
mkdir -p $FILENAME

source activate tensorflow_cdpm
# preprocessing, sampling the read
# satisfy the converage and length distritubtion requirement
echo "Executing the preprocessing step..."
python2 ./sampling_from_genome/sampling.py \
	-i $FULLFILE \
	-p ./$FILENAME/sampled_read \
	-n 10 \
	-d 2 \
	-c 0

# pore model translation
# convert the signal to the original range
# signal duplication 
# done within pore model
echo "Finished the preprocessing step!"
echo "Running the context-dependent pore model..."
rm -rf ./signal/*
mkdir -p ./signal
cd ./pore_model/src
python2 main.py \
	-i ../../$FILENAME/sampled_read.fasta \
	-p ../../signal/$PREFIX -t 20  \
	-a 0.1 -s 1
cd ../../	
# python ./pore_model/src/main.py \
# 	-i $FULLFILE \
# 	-p ./signal/$PREFIX -t 20  \
# 	-a 0.1 -s 0 \
# 	--perfect 1

# change the signal file to fasta5 file
echo "Finished generate the simulated signals!"
echo "Converting the signal into FAST5 files..."
rm -rf ./fast5/*
mkdir -p ./fast5
signal_dir="./signal/"
python2 ./signal_to_fast5/fast5_modify_signal.py \
	-i ./signal_to_fast5/template.fast5 \
	-s ${signal_dir} \
	-d ./fast5 

# basecalling using albacore

echo "Finished format converting!"
echo "Running Albacore..."
source activate basecall
FAST5_DIR="./fast5"
FASTQ_DIR="./fastq"
rm -rf $FASTQ_DIR/*
mkdir -p $FASTQ_DIR
read_fast5_basecaller.py -i $FAST5_DIR -s $FASTQ_DIR \
	-c r94_450bps_linear.cfg -o fastq -t 56

source activate tensorflow_cdpm

# check result
echo "Basecalling finished!"
echo "Checking the read accuracy..."
cp ./fastq/workspace/pass/*.fastq $FILENAME
cp ./fastq/workspace/pass/*.fastq ./mapping_check/test.fastq
./mapping_check/minimap2 -Hk19 -t 32 -c $FULLFILE \
	./mapping_check/test.fastq > ./mapping_check/mapping.paf

cd mapping_check
python2 acc_check.py
cd ..