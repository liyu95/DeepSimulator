#!/bin/bash

# ----- usage ------ #
usage()
{
	echo "Version 0.13 [2018-02-28] "
	echo "USAGE: ./trainingdata_generate.sh <-i DNA_SEQUENCE> <-p NANO_SIGNAL> [-o training_data]"
	echo "[note1]: DNA_SEQUENCE: (reference) sequence, such as 'ATCG...', in FASTA format"
	echo "         NANO_SIGNAL:   (nanopore) raw electrical current signal, in plain text"
	echo "[note2]: training_data: (output) training data, to train context-dependent pore model"
	echo "           by default, this file will be <name>.data where <name> is the input name of DNA_SEQUENCE"
	exit 1
}

if [ $# -lt 1 ];
then
        usage
fi
curdir="$(pwd)"



# ----- get arguments ----- #
#-> required arguments
DNA_SEQUENCE=""
NANO_SIGNAL=""
#-> optional arguments
training_data=""

#-> parse arguments
while getopts ":i:p:o:" opt;
do
	case $opt in
	#-> required arguments
	i)
		DNA_SEQUENCE=$OPTARG
		;;
	p)
		NANO_SIGNAL=$OPTARG
		;;
	#-> optional arguments
	o)
		training_data=$OPTARG
		;;
	#-> others
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


# ------ check required arguments ------ #
if [ ! -f "$DNA_SEQUENCE" ]
then
	echo "DNA_SEQUENCE $DNA_SEQUENCE not found !!" >&2
	exit 1
fi
if [ ! -f "$NANO_SIGNAL" ]
then
	echo "NANO_SIGNAL $NANO_SIGNAL not found !!" >&2
	exit 1
fi


# ------ related path ------ #
#-> get job id:
fulnam=`basename $DNA_SEQUENCE`
relnam=${fulnam%.*}


# ------ determine output file ----- #
if [ "$training_data" == "" ]
then
	training_data=$relnam.data
fi

# ============== main process ================== #

#-> use cwDTW to generate the alignment
./cwDTW_nano -i $DNA_SEQUENCE -p $NANO_SIGNAL -o $relnam.align 

#-> use Signal_To_Event_kmer to generate the training data
./Signal_To_Event $relnam.align > $training_data

#-> remove temporary file
rm -f $relnam.align


# ========= exit 0 =========== #
exit 0


