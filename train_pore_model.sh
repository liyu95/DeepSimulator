#!/bin/bash

# processing the input parameter
while [[ -n $1 ]]; do
        # echo "\$1=$1"
        case $1 in
                -i | --input )       shift
                                                INPUT=$1
                                                ;;
        esac
        shift
done
source $CONDA_PREFIX/etc/profile.d/conda.sh

# preprocessing
echo "Preprocess data..."
rm ./pore_model/data/example/*
cp -rf ${INPUT}/* ./pore_model/data/example/


cd ./pore_model/data/

ls ./example/*.fasta -1 | sed -e 's/\.fasta$//' > train_file.list
rm inter_data/*

while read line; do
	./trainingdata_generate.sh -i ${line}.fasta \
		-p ${line}.rawsig > log.txt 2> /dev/null
	#statements
done <  train_file.list
mv ./*.data ./inter_data/
rm -f log.txt
echo "Data preprocessing finished!!"


# run the pore model simulation part
cd ../src
conda activate tensorflow_cdpm
python2 main_train.py
conda deactivate
