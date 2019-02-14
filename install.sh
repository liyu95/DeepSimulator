#!/bin/bash


#-> 1. install tensorflow_cdpm
conda remove --name tensorflow_cdpm --all -y
conda create --name tensorflow_cdpm python=2.7 -y
source activate tensorflow_cdpm
pip install tensorflow==1.2.1
pip install tflearn==0.3.2
pip install tqdm==4.19.4
pip install scipy==0.18.1
pip install h5py==2.7.1
pip install numpy==1.13.1
pip install sklearn
source deactivate

#-> 2. install basecall
conda remove --name basecall --all -y
conda create --name basecall python=3.6 -y
source activate basecall
#wget -q https://mirror.oxfordnanoportal.com/software/analysis/ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl
pip install albacore_2.3.1/ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl
#rm -f ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl
source deactivate

