# DeepSimulator
The first deep learning based Nanopore simulator which can simulate the process of Nanopore sequencing.

Paper: https://academic.oup.com/bioinformatics/advance-article/doi/10.1093/bioinformatics/bty223/4962495

Reference:
```
@article{deepsimulator,
    author = {Li, Yu and Han, Renmin and Bi, Chongwei and Li, Mo and Wang, Sheng and Gao, Xin},
    title = {DeepSimulator: a deep simulator for Nanopore sequencing},
    journal = {Bioinformatics},
    volume = {34},
    number = {17},
    pages = {2899-2908},
    year = {2018},
    doi = {10.1093/bioinformatics/bty223},
    URL = {http://dx.doi.org/10.1093/bioinformatics/bty223},
    eprint = {/oup/backfile/content_public/journal/bioinformatics/34/17/10.1093_bioinformatics_bty223/2/bty223.pdf}
}

```

# Install
## Prerequisites
Anaconda2 (https://www.anaconda.com/distribution/) or Minoconda2 (https://conda.io/miniconda.html).
For example, users may download and install the following Anaconda2 package:
```
wget https://repo.anaconda.com/archive/Anaconda2-2018.12-Linux-x86_64.sh
bash Anaconda2-2018.12-Linux-x86_64.sh
```

## Download the DeepSimulator package
```
git clone https://github.com/realbigws/DeepSimulator.git
cd ./DeepSimulator/
```

## Install all required modules
```
./install
```

# Examples

## Context-dependent pore model
```
./pore_model.sh example/001c577a-a502-43ef-926a-b883f94d157b.true_fasta 0
```

## Context-independent kmer pore model (using official 6mer)
```
./pore_model.sh example/001c577a-a502-43ef-926a-b883f94d157b.true_fasta 1
```

## Simulate the signal and read for a given sequence
```
./deep_simulator.sh -i example/001c577a-a502-43ef-926a-b883f94d157b.true_fasta -n -1
```

## Run a test to generate simulated signals and reads for a given genome
```
./deep_simulator.sh -i example/artificial_human_chr22.fasta
```

# Simulated VS original signal

## Simulated signal

![alt text](https://github.com/realbigws/DeepSimulator/blob/master/example/simulated_signal.png)

## Original signal
![alt text](https://github.com/realbigws/DeepSimulator/blob/master/example/original_signal.png)


## Control the behavior of DeepSimulator
One can control the behavior of DeepSimulator, including the length distribution of the reads or the accuracy, *etc.*, by using different options in ```deep_simulator.sh```. Detailed descriptions of the parameters in ```deep_simulator.sh``` file can be refered to Section S4 in [Supplementary material of DeepSimulator](https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/bioinformatics/34/17/10.1093_bioinformatics_bty223/2/bty223_supplemental_materials.pdf?Expires=2147483647&Signature=v5FSUbbU4eVfQdIo3H3Xrsq6CFVh8azonSxGg1WaAL35maQ0zqIPzdRPTTGUUhlzkLYBnU3Fi4G1DRcXc5YDD4Ea~8ic56zpjBNWQ4qqSZabjH9XwTFyPTbh6IKaHkULi9zKfSl02MxxXfqEJ0Xi72AKRv0Up4j~baWrfyUEKYtEVkzJbpbyAsnZhvPh2WSbFXyPhRhBn~fH9XfrEO9hbMQPSrT9di2Ho85ZBbZ2xS0P~J8sZyi91ulXQHfYSH5rbdaTNAAxRCVbLQUi3iKbJFE5Bl0de66w0mdjfgIZGqrBY9uPoXwW4MYf6H7OwmVXnDc-sjoe73UxO4xHRF17Ag__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA)

# Train customized model

## Simple example
Our simulator supports training a pore model using a customized dataset. An simple example, which only used the CPU resource, would be like this:
```
./train_pore_model.sh -i customerized_data/
```
Within the data folder, there are two kinds of data should be provided. The first kind of data is the sequence, and the second kind of data is the corresponding nanopore raw signal. Users can find an example of each file in the 'customized_data' folder.
After training, an model (three files, named "model_customized.ckpt\*") would be generated in the folder 'pore_model/model'. The user can rename the build-in model (named "model_reg_seqs_gn179.ckpt\*"") to a backup name and the customized model as "model_reg_seqs_gn179.ckpt\*" (all the three files need to be changed accordingly) so that the user do not have to change the code of simulator to use the customized model.

**Notice**: Generally, we do not recommend user to train a customized pore model because the data preparation and model training are quite time consuming and there might be some unexpected errors because  of the update of Tensorflow and the dependencies, such as CUDA and cuDNN, which notoriously annoying. We would make the model updated to the Nanopore technology development.

## Advanced
The above example only uses CPU, which would take years to train a model. To accelerate the training process and take advantage the computational power of GPU, users can consider using the GPU version of Tensorflow. User should make sure the following dependencies are installed correctly before running the training code on a workstation with GPU card.

1. CUDA (http://docs.nvidia.com/cuda/cuda-installation-guide-linux/#axzz4VZnqTJ2A)
2. cuDNN (https://developer.nvidia.com/cudnn)
3. Tensorflow-gpu (https://www.tensorflow.org/install/install_linux)

Users can refer to the Tensorflow website (https://www.tensorflow.org/) for more detailed instruction of setting up the environment.

*This tool is for academic purposes and research use only. Any commercial use is subject for authorization from King Abdullah University of Science and technology “KAUST”. Please contact us at ip@kaust.edu.sa.*
