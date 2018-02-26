This module would use the BLAST from NCBI (bl2seq).
The full documentation of bl2seq could be referred to the NCBI website.

The other files in this folder are just doing the file preprocessing and file postprocessing.

**If users would just like to have a basic understanding of the overall quality of the simulated reads, we would recommend users to use the build-in minimap2 module, which is staightforward, quick and simple.**

Notice that this module would evaluate the reads start from module 2 until the end. So we need to collect the output of module 1, which is the ground truth and the output of module 3, which is the final simulated reads. Besides, we also need a name mapping between the two outputs.
We can use
```
cd fasta5
ls . > mapping.txt
```
to get the name mapping.

Then move the ground truth to this folder and rename it to 'test.fasta', move the final fastq file to this folder and rename it to 'test.fastq', and move the mapping.txt file to this folder as well.

Then run
```
./main.sh
```


The final result is store in 'result.txt'. For full explanation of the file format, please refer to the NCBI website.