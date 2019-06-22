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

# CPU number
THREADNUM=32

# the input should be a fasta file
# we should make a tmp directory named after the input file to
# store the tmp files
mkdir -p $FILENAME

source activate tensorflow_cdpm
# preprocessing, sampling the read
# satisfy the converage and length distritubtion requirement
echo "Executing the preprocessing step..."

python2 ./util/genome_preprocess.py \
	-i $FULLFILE \
	-o $FILENAME/processed_genome \
	-r 1

python2 ./util/genome_sampling.py \
	-i $FILENAME/processed_genome \
	-p $FILENAME/sampled_read \
	-n 100 \
	-K 0 \
	-l 8000 \
	-d 3 \
	-S 0 

# pore model translation
# convert the signal to the original range
# signal duplication 
# done within pore model
echo "Finished the preprocessing step!"
echo "Running the context-dependent pore model..."
rm -rf $FILENAME/signal/*
mkdir -p $FILENAME/signal
rm -rf $FILENAME/align/*
mkdir -p $FILENAME/align
rm -rf $FILENAME/fast5/*
mkdir -p $FILENAME/fast5

curdir="$(pwd)"

export DeepSimulatorHome=$curdir
python2 ./pore_model/src/context_simulator.py \
	-i $FILENAME/sampled_read.fasta \
	-p $FILENAME/signal/signal \
	-l $FILENAME/align/align \
	-t $THREADNUM \
	-f 950 -s 1.0 \
	-S 0 \
	-u 1 \
	-F $FILENAME/fast5 \
	-T ./util/template.fast5


# change the signal file to fasta5 file
# echo "Finished generate the simulated signals!"
# echo "Converting the signal into FAST5 files..."
# rm -rf ./fast5/*
# mkdir -p ./fast5
# signal_dir="./signal/"
# python2 ./signal_to_fast5/fast5_modify_signal.py \
# 	-i ./signal_to_fast5/template.fast5 \
# 	-s ${signal_dir} \
# 	-d ./fast5 

# basecalling using albacore

echo "Finished format converting!"
echo "Running Albacore..."
source activate basecall
FAST5_DIR="$FILENAME/fast5"
FASTQ_DIR="$FILENAME/fastq"
rm -rf $FASTQ_DIR/*
mkdir -p $FASTQ_DIR
read_fast5_basecaller.py -i $FAST5_DIR -s $FASTQ_DIR \
	-c r94_450bps_linear.cfg -o fastq -t $THREADNUM

source activate tensorflow_cdpm

# check result
echo "Basecalling finished!"
echo "Checking the read accuracy..."


cat $FILENAME/fastq/workspace/pass/*.fastq > $FILENAME/pass.fastq 2>$FILENAME/err
cat $FILENAME/fastq/workspace/fail/*.fastq > $FILENAME/fail.fastq 2>$FILENAME/err

pass_num=`grep "^@" $FILENAME/pass.fastq | wc | awk '{print $1}'`
fail_num=`grep "^@" $FILENAME/fail.fastq | wc | awk '{print $1}'`
cat $FILENAME/pass.fastq $FILENAME/fail.fastq > $FILENAME/test.fastq
./util/minimap2 -Hk19 -t $THREADNUM -c $FULLFILE \
	$FILENAME/test.fastq 1> $FILENAME/mapping.paf 2> $FILENAME/err
rm -f $FILENAME/err
accuracy=`awk 'BEGIN{a=0;b=0}{a+=$10/$11;b++}END{print a/b}' $FILENAME/mapping.paf`
totalnum=`grep "^@" $FILENAME/test.fastq | wc | awk '{print $1}'`
echo "Here is the mapping identity: $accuracy of $totalnum (pass $pass_num + fail $fail_num) reads passed base-calling."
echo "$accuracy $totalnum $pass_num $fail_num" > $FILENAME/accuracy
# remove temporary files
rm -rf $FILENAME/fastq
rm -f $FILENAME/test.fastq

#---------- exit -----------#
exit 0
