#!/bin/bash

# ----- usage ------ #
function usage()
{
	echo "DeepSimulator v1.5 [Jun-29-2019] "
	echo "    A Deep Learning based Nanopore simulator which can simulate the process of Nanopore sequencing. "
	echo ""
	echo "USAGE:  ./deep_simulator.sh <-i input_genome> [-o out_root] [-c CPU_num] [-S random_seed] [-B basecaller] "
	echo "                [-n read_num] [-K coverage] [-l read_len_mean] [-C cirular_genome] [-m sample_mode] "
	echo "                [-M simulator] [-e event_std] [-u tune_sampling] [-O out_align] [-G sig_out]"
	echo "                [-f filter_freq] [-s signal_std] [-P perfect] [-H home] "
	echo "Options:"
	echo ""
	echo "***** required arguments *****"
	echo "-i input_genome   : input genome in FASTA format. "
	echo ""
	echo "***** optional arguments (main) *****"
	echo "-o out_root       : Default output would the current directory. [default = './\${input_name}_DeepSimu'] "
	echo ""
	echo "-c CPU_num        : Number of processors. [default = 8]"
	echo ""
	echo "-S random_seed    : Random seed for controling the simulation process. [default = 0]"
	echo "                    0 for a random seed. Use other number for a fixed seed for reproducibility. "
	echo ""
	echo "-B basecaller     : Choose from the following basecaller for the basecalling process. [default = 1] "
	echo "                    1: guppy_gpu, 2: guppy_cpu, 3: albacore."
	echo ""
	echo "***** optional arguments (read-level) *****"
	echo "-n read_num       : The number of reads need to be simulated. [default = 100] "
	echo "                    Set -1 to simulate the whole input sequence without cut (not suitable for genome-level). "
	echo ""
	echo "-K coverage       : This parameter is converted to number of read in the program. [default = 0] "
	echo "                    If both K and n are given, we use the larger one."
	echo ""
	echo "-l read_len_mean  : This parameter is used to control the read length mean. [default=8000] "
	echo ""
	echo "-C cirular_genome : 0 for linear genome and 1 for circular genome. [default = 0] "
	echo ""
	echo "-m sample_mode    : Choose from the following distribution for the read length. [default = 3] "
	echo "                    1: beta_distribution, 2: alpha_distribution, 3: mixed_gamma_dis. "
	echo ""
	echo "***** optional arguments (event-level) *****"
	echo "-M simulator      : Choose context-dependent(0) or context-independent(1) simulator to generate event. [default = 1] "
	echo ""
	echo "-e event_std      : Set the standard deviation (std) of the random noise of the event. [default = 1.0] "
	echo ""
	echo "-u tune_sampling  : Tuning sampling rate to around eight for each event. [default = 1 to tune] "
	echo "                    Here eight is determined by 4000/450, where 4KHz is the signal sampling frequency, "
	echo "                    and 450 is the bases per second to pass the nanopore. "
	echo ""
	echo "-O out_align      : Output ground-truth warping path between simulated signal and event. [default = 0 NOT to output] "
	echo ""
	echo "-G out_signal     : Output simulated signal in txt format. [default = 0 NOT to output] "
	echo ""
	echo "***** optional arguments (signal-level) *****"
	echo "-f filter_freq    : Set the cutoff frequency for the low-pass filter. [default = 950] "
	echo "                    [hint]: a higher cutoff frequency value would result in better base-calling accuracy. "
	echo ""
	echo "-s signal_std     : Set the standard deviation (std) of the random noise of the signal. [default = 1.0] "
	echo "                    [hint]: tune event_std, filter_freq and signal_std to simulate different sequencing qualities. "
	echo ""
	echo "-P perfect        : 0 for normal mode (with length repeat and random noise). [default = 0]"
	echo "                    1 for generating almost perfect reads without any randomness in signals (equal to -e 0 -f 0 -s 0). "
	echo ""
	echo "***** home directory *****"
	echo "-H home           : Home directory of DeepSimulator. [default = 'current directory'] "
	echo ""
	exit 1
}


#------------------------------------------------------------#
##### ===== get pwd and check BlastSearchHome ====== #########
#------------------------------------------------------------#

#------ current directory ------#
curdir="$(pwd)"

#-------- check usage -------#
if [ $# -lt 1 ];
then
        usage
fi


#---------------------------------------------------------#
##### ===== All arguments are defined here ====== #########
#---------------------------------------------------------#

#------- required arguments ------------#
FULLFILE=""
out_root=""
#------- optioanl parameters -----------#
THREAD_NUM=8        #-> this is the thread (or, CPU) number
RANDOM_SEED=0       #-> random seed for controling sampling, for reproducibility. default: [0]
BASE_CALLER=1       #-> choose from the following basecaller: 1: guppy_gpu, 2: guppy_cpu, 3: albacore. default: [1]
#------- read-level parameter ----------#
SAMPLE_NUM=100      #-> by default, we simulate 100 reads
COVERAGE=0          #-> the coverage parameter, we simulate read whichever the larger, SAMPLE_NUM or the number computed from coverage
LEN_MEAN=8000       #-> read length mean
GENOME_CIRCULAR=0   #-> 0 for NOT circular and 1 for circular. default: [0]
SAMPLE_MODE=3       #-> choose from the following distribution: 1: beta_distribution, 2: alpha_distribution, 3: mixed_gamma_dis. default: [3]
#------- event-level parameter ---------#
SIMULATOR_MODE=1    #-> choose from the following type of simulator: 0: context-dependent, 1: context-independent. default: [1]
EVENT_STD=1.0       #-> set the std of random noise of the event, default = 1.0
TUNE_SAMPLING=1     #-> 1 for tuning sampling rate to around 8. default: [1]
ALIGN_OUT=0         #-> 1 for the output of ground-truth warping path between simulated signal and event. default: [0]
SIG_OUT=0           #-> 1 to output the signal in text format
#------- signal-level parameter --------#
FILTER_FREQ=950     #-> set the cutoff frequency for the low-pass filter. default = 950
NOISE_STD=1.0       #-> set the std of random noise of the signal, default = 1.0
#-> perfect mode
PERFECT_MODE=0      #-> 0 for normal mode (with length repeat and random noise). [default = 0]
                    #-> 1 for generating almost perfect reads without any randomness in signals (equal to -e 0 -f 0 -s 0).
#------- home directory ----------------#
home=`dirname $0`   #-> home directory


#------- parse arguments ---------------#
while getopts ":i:o:c:S:B:n:K:l:C:m:M:e:u:O:G:f:s:P:H:" opt;
do
	case $opt in
	#-> required arguments
	i)
		FULLFILE=$OPTARG
		;;
	#-> optional arguments
	o)
		out_root=$OPTARG
		;;
	c)
		THREAD_NUM=$OPTARG
		;;
	S)
		RANDOM_SEED=$OPTARG
		;;
	B)
		BASE_CALLER=$OPTARG
		;;
	#-> read-level arguments
	n)
		SAMPLE_NUM=$OPTARG
		;;
	K)
		COVERAGE=$OPTARG
		;;
	l)
		LEN_MEAN=$OPTARG
		;;
	C)
		GENOME_CIRCULAR=$OPTARG
		;;
	m)
		SAMPLE_MODE=$OPTARG
		;;
	#-> event-level arguments
	M)
		SIMULATOR_MODE=$OPTARG
		;;
	e)
		EVENT_STD=$OPTARG
		;;
	u)
		TUNE_SAMPLING=$OPTARG
		;;
	O)
		ALIGN_OUT=$OPTARG
		;;
	G)
		SIG_OUT=$OPTARG
		;;
	#-> signal-level parameters
	f)
		FILTER_FREQ=$OPTARG
		;;
	s)
		NOISE_STD=$OPTARG
		;;
	P)
		PERFECT_MODE=$OPTARG
		;;
	#-> home directory
	H)
		home=$OPTARG
		;;
	#-> default
	\?)
		echo "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	:)
		echo "Option -$OPTARG requires an argument." >&2
		exit 1
		;;
	esac
done



#---------------------------------------------------------#
##### ===== Part 0: initial argument check ====== #########
#---------------------------------------------------------#

# ------ check home directory ---------- #
if [ ! -d "$home" ]
then
	echo "home directory $home not exist " >&2
	exit 1
fi
home=`readlink -f $home`

#----------- check input genome  -----------#
if [ ! -s "$FULLFILE" ]
then
	echo "input input_genome is null !!" >&2
	exit 1
fi
FULLFILE=`readlink -f $FULLFILE`
#-> get query_name
fulnam=`basename $FULLFILE`
relnam=${fulnam%.*}

# ------ check output directory -------- #
if [ "$out_root" == "" ]
then
	out_root=${relnam}_DeepSimu
fi
mkdir -p $out_root
out_root=`readlink -f $out_root`


#--------------------------------------------------------#
##### ===== Part 1: DeepSimulator process ====== #########
#--------------------------------------------------------#

#------- init process -----------------#
FILENAME=$out_root
NUM=$(fgrep -o '>' $FULLFILE | wc -l)
PREFIX="signal"
PREALI="align"

# the input should be a fasta file
# we should make a tmp directory named after the input file to
# store the tmp files
echo "Pre-process input genome..."
source activate tensorflow_cdpm
python2 $home/util/genome_preprocess.py \
	-i $FULLFILE \
	-o $FILENAME/processed_genome \
	-r 1
source deactivate
echo "Pre-process input genome done!"

# preprocessing, sampling the read
# satisfy the converage and length distritubtion requirement
echo "Executing the preprocessing step..."
circular=""
if [ $GENOME_CIRCULAR -eq 1 ]
then
	circular="-c True"
fi
if [ $SAMPLE_NUM -gt 0 ]
then
	source activate tensorflow_cdpm
	python2 $home/util/genome_sampling.py \
		-i $FILENAME/processed_genome \
		-p $FILENAME/sampled_read \
		-n $SAMPLE_NUM \
		-K $COVERAGE \
		-l $LEN_MEAN \
		-d $SAMPLE_MODE \
		-S $RANDOM_SEED \
		$circular
	source deactivate
else
	cp $FILENAME/processed_genome $FILENAME/sampled_read.fasta
fi
echo "Finished the preprocessing step!"

# pore model translation
# convert the signal to the original range
# signal duplication 
# done within pore model
rm -rf $FILENAME/signal/*
if [ $SIG_OUT -eq 1 ]
then
	mkdir -p $FILENAME/signal
fi
rm -rf $FILENAME/align/*
if [ $ALIGN_OUT -eq 1 ]
then
	mkdir -p $FILENAME/align
fi

#--------- determine running mode -----------#
#-> output alignment
align_out=""
if [ $ALIGN_OUT -eq 1 ]
then
	align_out="--outali True"
fi
sig_out=""
if [ $SIG_OUT -eq 1 ]
then
	sig_out="--sigout True"
fi
#-> perfect mode
perf_mode=""
if [ $PERFECT_MODE -eq 1 ]
then
	EVENT_STD=0
	FILTER_FREQ=0
	NOISE_STD=0
fi
#-> official kmer model
model_file=template_median68pA.model
#-> default fast5 template
fast5_template=template.fast5

#--------- run different mode of simulator -------------#
echo "Key parameters for simulation are shown below "
echo "    event_std    : $EVENT_STD "
echo "    filter_freq  : $FILTER_FREQ "
echo "    signal_std   : $NOISE_STD "
rm -rf $FILENAME/fast5/*
mkdir -p $FILENAME/fast5
if [ $SIMULATOR_MODE -eq 0 ]
then
	echo "Running the context-dependent pore model..."
	#-> context-dependent simulator
	source activate tensorflow_cdpm
	export DeepSimulatorHome=$home
	python2 $home/pore_model/src/context_simulator.py \
		-i $FILENAME/sampled_read.fasta \
		-p $FILENAME/signal/$PREFIX \
		-l $FILENAME/align/$PREALI \
		-t $THREAD_NUM  \
		-f $FILTER_FREQ -s $NOISE_STD \
		-S $RANDOM_SEED \
		-u $TUNE_SAMPLING \
		-F $FILENAME/fast5 \
		-T $home/util/$fast5_template \
		$perf_mode $align_out $sig_out
	source deactivate
else
	echo "Running the context-independent pore model..."
	#-> contect-independent simulator
	source activate tensorflow_cdpm
	python2 $home/pore_model/src/kmer_simulator.py \
		-i $FILENAME/sampled_read.fasta \
		-p $FILENAME/signal/$PREFIX \
		-l $FILENAME/align/$PREALI \
		-t $THREAD_NUM -m $home/pore_model/model/$model_file \
		-e $EVENT_STD -f $FILTER_FREQ -s $NOISE_STD \
		-S $RANDOM_SEED \
		-u $TUNE_SAMPLING \
		-F $FILENAME/fast5 \
		-T $home/util/$fast5_template \
		$perf_mode $align_out $sig_out
	source deactivate
fi
echo "Finished generate the simulated signals and fast5 files!"

#--------- base-calling ----------------#
#-> guppy version
guppy=guppy_3.1.5
# basecalling using guppy_gpu by dfault
echo "Running Basecalling..."
FAST5_DIR="$FILENAME/fast5"
FASTQ_DIR="$FILENAME/fastq"
rm -rf $FASTQ_DIR/*
mkdir -p $FASTQ_DIR
# run different base-callers
if [ $BASE_CALLER -eq 1 ]
then
	echo "   Basecalling with Guppy_GPU..."
	$home/base_caller/$guppy/ont-guppy/bin/guppy_basecaller -r --input_path $FAST5_DIR \
		--save_path $FASTQ_DIR -c dna_r9.4.1_450bps_hac.cfg \
		-x auto
elif [ $BASE_CALLER -eq 2 ]
then
	echo "   Basecalling with Guppy_CPU..."
	$home/base_caller/$guppy/ont-guppy-cpu/bin/guppy_basecaller -r --input_path $FAST5_DIR \
		--save_path $FASTQ_DIR -c dna_r9.4.1_450bps_hac.cfg \
		--cpu_threads_per_caller $THREAD_NUM --num_callers 1
else
	echo "   Basecalling with Albacore..."
	source activate basecall
	read_fast5_basecaller.py -i $FAST5_DIR -s $FASTQ_DIR \
		-c r94_450bps_linear.cfg -o fastq -t $THREAD_NUM
	source deactivate
fi
echo "Basecalling finished!"

#--------- calculate accuracy ----------#
# check result
echo "Checking the read accuracy..."
if [ $BASE_CALLER -eq 3 ]
then
	cat $FILENAME/fastq/workspace/pass/*.fastq > $FILENAME/pass.fastq 2>$FILENAME/err
	cat $FILENAME/fastq/workspace/fail/*.fastq > $FILENAME/fail.fastq 2>$FILENAME/err
else
	cat $FILENAME/fastq/*.fastq > $FILENAME/pass.fastq 2>$FILENAME/err
	touch $FILENAME/fail.fastq
fi
pass_num=`grep "^@" $FILENAME/pass.fastq | wc | awk '{print $1}'`
fail_num=`grep "^@" $FILENAME/fail.fastq | wc | awk '{print $1}'`
cat $FILENAME/pass.fastq $FILENAME/fail.fastq > $FILENAME/test.fastq
$home/util/minimap2 -Hk19 -t $THREAD_NUM -c $FULLFILE \
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

