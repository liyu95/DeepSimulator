#!/bin/bash

if [ -f "cwDTW_nano" ] 
then
	echo " executable files 'cwDTW_nano' already compiled "
	exit 1
fi


mkdir -p Release
cd Release
cmake -DCMAKE_BUILD_TYPE=Release ..
make
mv bin/wletdtw ../cwDTW_nano
cd ../
rm -rf Release


