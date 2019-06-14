#-> ont-guppy-cpu
if [ ! -d "ont-guppy-cpu" ]
then
	wget -q https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy-cpu_3.1.5_linux64.tar.gz
	tar xzf ont-guppy-cpu_3.1.5_linux64.tar.gz
	rm -f ont-guppy-cpu_3.1.5_linux64.tar.gz
fi

#-> ont-guppy
if [ ! -d "ont-guppy" ]
then
	wget -q https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_3.1.5_linux64.tar.gz
	tar xzf ont-guppy_3.1.5_linux64.tar.gz
	rm -f ont-guppy_3.1.5_linux64.tar.gz
fi

