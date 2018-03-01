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


# preprocessing
rm ./pore_model/data/example/*
cp -rf ${INPUT}/* ./pore_model/data/example/


cd ./pore_model/data/

ls ./example/*.fasta -1 | sed -e 's/\.fasta$//' > train_file.list
rm inter_data/*

while read line; do
	./trainingdata_generate.sh -i ${line}.fasta \
		-p ${line}.rawsig
	#statements
done <  train_file.list
mv ./*.data ./inter_data/

# run the pore model simulation part
cd ../src
python2 main_train.py