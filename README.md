# DeepSimulator
The first deep learning based Nanopore simulator which can simulate the process of Nanopore sequencing.


# Prerequisites
1. Anaconda 2 or Minoconda 2 (https://conda.io/miniconda.html)
2. Downloaded Albacore (Suppose you downloaded: ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl: https://mirror.oxfordnanoportal.com/software/analysis/ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl)

# Build a virtual environment for Albacore basecalling
```
<!-- This the python version should be the same as the Albacore you downloaded -->
conda create -n basecall python=3.6
<!-- Install the Albacore using pip -->
<!-- Make sure the .whl file is in the current directory -->
source activate basecall
pip install ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl
source deactivate
```

# Download the DeepSimulator package
```
git clone https://github.com/lykaust15/DeepSimulator.git
cd ./DeepSimulator/
```

# Build a virtual environment for the context-independent pore model
```
conda env create -f environment.yml
```

# Run a test
```
./main.sh -f ./test_samples/human_single.fasta
```
<!-- Remember to save the fast5 folder since it is consider to be a temp folder and overwritten every time you run the main.sh file -->