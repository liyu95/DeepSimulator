# DeepSimulator
The first deep learning based Nanopore simulator which can simulate the process of Nanopore sequencing.

# Prerequisites
1. Python 2.7
2. Anaconda 2 or Minoconda 2 (This is for build the environment of Albacore. If you choose to use other basecaller, then this one can be ignored.)
3. Downloaded Albacore (Suppose you downloaded: ont_albacore-2.0.2-cp36-cp36m-manylinux1_x86_64.whl)

# Build a virtual environment for Albacore basecalling
```
<!-- This the python version should be the same as the Albacore you downloaded -->
conda create -n basecall python=3.6
<!-- Install the Albacore using pip -->
pip install ont_albacore-2.0.2-cp36-cp36m-manylinux1_x86_64.whl --user
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