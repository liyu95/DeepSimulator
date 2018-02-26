#!/bin/bash

#-> input files
mapping_txt=mapping.txt
all_test_fasta=test.fasta
test_fastq=test.fastq

#-> 0. create directory
rm -rf Ground_truch
rm -rf Decode_sequence
mkdir -p Ground_truch
mkdir -p Decode_sequence 

#-> 1. get list
awk -F '[_.]' '{print $2}' ${mapping_txt} > wslist1
awk -F '[_.]' '{print $3}' ${mapping_txt} > wslist2
awk -F '[_.]' '{print $2"|"$3}' ${mapping_txt} > wslist3

extract_1(){
	local i=$1
	a=`grep $i -A 1 ${all_test_fasta} | tail -n1`
	echo ">$i" > Ground_truch/$i.fasta
	echo $a >> Ground_truch/$i.fasta
}

extract_2(){
	local i=$1
	a=`grep $i -A 1 ${test_fastq} | tail -n1`
	echo ">$i" > Decode_sequence/$i.fasta
	echo $a >> Decode_sequence/$i.fasta
}

#-> 2. extract sequences
for i in `cat wslist1`; 
do 
extract_1 "$i" &
done
for i in `cat wslist2`;  
do
extract_2 "$i" &
done

echo 'extract sequences finished!'

blast(){
local i=$1
a=`echo $i | cut -d '|' -f 1`
b=`echo $i | cut -d '|' -f 2`
c=`./bl2seq -i Ground_truch/$a.fasta -j Decode_sequence/$b.fasta -p blastn -D 1 | grep -v "#" | head -n1`
echo "$i $c" >> fufufufout
}
#-> 3. run BLAST
rm -f fufufufout
for i in `cat wslist3`; 
do  
blast "$i"
done

#-> 4. calculate accuracy
awk '{if(NF==13){print $0}}' fufufufout > result.txt
./Stat_List result.txt 3 

