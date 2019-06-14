conda remove --name basecall --all -y
conda create --name basecall python=3.6 -y
source activate basecall
wget -q https://mirror.oxfordnanoportal.com/software/analysis/ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl
pip install ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl
rm -f ont_albacore-2.3.1-cp36-cp36m-manylinux1_x86_64.whl

