# DeepSimulator
The first deep learning based Nanopore simulator which can simulate the process of Nanopore sequencing.

# Usage
## Prerequisites
1. Anaconda 2 or Minoconda 2 (https://conda.io/miniconda.html)
2. Downloaded Albacore (Suppose you downloaded: ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl: https://mirror.oxfordnanoportal.com/software/analysis/ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl)

## Build a virtual environment for Albacore basecalling
```
<!-- This the python version should be the same as the Albacore you downloaded -->
conda create -n basecall python=3.6
<!-- Install the Albacore using pip -->
<!-- Make sure the .whl file is in the current directory -->
source activate basecall
pip install ont_albacore-2.1.3-cp36-cp36m-manylinux1_x86_64.whl
source deactivate
```

## Download the DeepSimulator package
```
git clone https://github.com/lykaust15/DeepSimulator.git
cd ./DeepSimulator/
```

## Build a virtual environment for the context-independent pore model
```
<!-- This step may take up to 8 mins since it would install all the dependencies -->
conda env create -f environment.yml
```

## Run a test
```
./main.sh -f ./test_samples/human_single.fasta
```
<!-- Remember to save the fast5 folder since it is consider to be a temp folder and overwritten every time you run the main.sh file -->

# Train our model
## Dependency
User should make sure the the following dependencies are installed correctly before running the training code.
```
CUDA (http://docs.nvidia.com/cuda/cuda-installation-guide-linux/#axzz4VZnqTJ2A)
cuDNN (https://developer.nvidia.com/cudnn)
Tensorflow (https://www.tensorflow.org/install/install_linux)
```

Our simulator supports training a pore model using a customized dataset. An example is like this:
```
./train_pore_model.sh -i data_folder
```
Within the data folder, there are two kinds of data should be provided. The first kind of data is the sequence, and the second kind of data is the corresponding nanopore raw signal. Users can find an example of each file in the 'customized_data' folder.
After training, an model would be generated in the folder 'pore_model/model'. The user can rename the build-in model as a backup name and the customized model as the original name as the build-in model so that the user do not have to change the code of simulator to use the customized model.

**Notice**: generally, we do not recommend user to train a customized pore model because the data preparation and model training are quite time consuming and there might be some unexpected errors because  of the update of Tensorflow and the dependencies, such as CUDA and cuDNN.

*This tool is for academic purposes and research use only. Any commercial use is subject for authorization from King Abdullah University of Science and technology “KAUST”. Please contact us at ip@kaust.edu.sa.*