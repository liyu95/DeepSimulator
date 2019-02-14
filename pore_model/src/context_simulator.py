from data_pre import *
from con_reg_seq import *
from poremodel_util import *
import numpy as np
from multiprocessing import Pool
import multiprocessing
import os
import argparse
import tqdm


#----- use GPU for TensorFlow -----#
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


#--------------- generate chunk seq ---------------#
def generate_chunk_seq(sequence, chunk_size=100, stride=100):
    num_full_chunk = int((float(len(sequence)-4)/stride))
    sequence_list = list()
    # deal with extremely short sequence
    if len(sequence)==0:
        sys.exit('The sequence length is ZERO!!')
    if num_full_chunk==0:
        single_chunk = np.tile(sequence, (chunk_size+4, 1))
        sequence_list.append(single_chunk[:chunk_size+4])
        return np.array(sequence_list)

    for i in range(num_full_chunk):
        sequence_list.append(sequence[i*stride:i*stride+chunk_size+4])
    # deal with the small chunk, using mirrioning to get a full chunk
    if(len(sequence)!=(num_full_chunk*stride+4)):
        remainder = len(sequence)-(num_full_chunk*stride+4)
        add_chunk= sequence[-(remainder+2):]
        comp_chunk = np.flip(sequence[-(chunk_size-remainder+2):],0)
        add_chunk = np.vstack((add_chunk,comp_chunk))
        sequence_list.append(add_chunk)
    return np.array(sequence_list)

def convert_to_input(seq_list):
    p = Pool()
    encoding_list = map(sequence_encoding, seq_list)
    seq_chunk_list = p.map(generate_chunk_seq, encoding_list)
    p.close()
    p.join()
    return seq_chunk_list


#----------- main program: sequence to raw signal --------------#
# default parameters:
#     repeat_alpha=0.1
#     filter_freq=850
#     noise_std=1.5
def raw_to_true_signal(result_pred, sequence, repeat_alpha, filter_freq, noise_std, perfect, p_len):
    result_pred = np.array(result_pred)
    result_pred = result_pred.flatten()
    final_result = result_pred[:len(sequence)]   #-> this is Z-score
    final_result = np.array(final_result*12.868652 + 90.208199)
    #--- add gauss noise ----#
    if perfect:
        final_result, final_ali = repeat_k_time(p_len, final_result)
    else:
        #-> 1. repeat N times
        final_result, final_ali, _ = repeat_n_time(repeat_alpha, final_result)
        #-> 2. low pass filter
        if filter_freq>0:
            h,h_start,N = low_pass_filter(4000.0, filter_freq, 40.0)
            final_result = np.convolve(final_result,h)[h_start+1:-(N-h_start-1)+1]
        #-> 3. add gauss noise
        if noise_std>0:
            final_result = final_result + add_noise(noise_std, len(final_result))
    #--- make integer -------#
    final_result = np.array(final_result)
    final_result = np.array(map(int, 5.7*final_result+14))
    return final_result, final_ali




#=================== main =======================#
if __name__ == '__main__':
	os.environ['CUDA_VISIBLE_DEVICES'] ='-1'

	#--------- argument part -------------#
	parser = argparse.ArgumentParser(description='convert the \
		input sequence to nanopore signal')
	parser.add_argument('-i', action='store', dest='input', required=True, 
		help='the input file')
	parser.add_argument('-p', action='store', dest='output', required=True,
		help='prefix the output file')
	parser.add_argument('-l', action='store', dest='alignment', required=True,
		help='prefix the alignment file')
	parser.add_argument('-t', action='store', dest='threads',
		type=int, help='the number of threads used', default=1)
	parser.add_argument('-a', action='store', dest='alpha',
		type=float, help='change the distribution of the signal repeat time, \
		value between 0 and 1, 0.1 (default) would give the distribution best \
		simulate the real case, 0 would give distribution whose basecalling \
		result is slightly worse than the real case, 1 would give the almost \
		perfect basecalling result using Albacore', default=0.1)
	parser.add_argument('-s', action='store', dest='std',
		type=float, help='set the std of the signal. \
		The higher the value, the blurred the signal. (default is 1.5)',
		default=1.5)
	parser.add_argument('-f', action='store', dest='freq',
		type=float, help='change the cut frequency in the low pass filter. \
		The higher the value, the smoother the signal. (default is 850)',
		default=850)
	parser.add_argument('--perfect', action='store', dest='perfect',
		type=bool, help='Do you want a perfect signal and sequence',
		default=False)
	parser.add_argument('--perflen', action='store', dest='perflen',
		type=int, help='repeat length for perfect mode',
		default=1)

	#---------- input list ---------------#
	arg = parser.parse_args()
	seq_list = get_seq_list(arg.input)
	id_list = get_id_list(arg.input)
	seq_chunk_list = convert_to_input(seq_list)

	#---------- deep simulator -----------#
	result_list = []
	p = Pool(arg.threads)
	result_list = list(tqdm.tqdm(
		p.imap(model_whole_set_check, seq_chunk_list), 
		total=len(seq_chunk_list)))
	p.close()
	p.join()

	#---------- output results -----------#
	for i in range(len(result_list)):
		final_signal, final_ali = raw_to_true_signal(result_list[i], 
			seq_list[i], arg.alpha, arg.freq, arg.std, arg.perfect, arg.perflen)
		write_output(final_signal, arg.output+'_{}.txt'.format(id_list[i]))
		if not arg.perfect:
			write_alignment(final_ali, arg.alignment+'_{}.ali'.format(id_list[i]))

