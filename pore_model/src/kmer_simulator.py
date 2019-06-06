from poremodel_util import *
import numpy as np
from functools import partial
from multiprocessing import Pool
import multiprocessing
import argparse
from tqdm import *


#--------------- step 0: official kmer pore model ---------#
#-> load plain text file for official pore model
#   data structure is a dict with 4096 dims (6mer 4^6)
#   data.keys()   :   kmer
#   data.values() :   (mean, vari)
#-> the file 'template_median68pA.model' could be downloaded from
#   https://github.com/nanoporetech/kmer_models/blob/master/r9.4_180mv_450bps_6mer/template_median68pA.model
def load_official_poremodel(input_file):
    model_data = np.genfromtxt(input_file, delimiter="\t", dtype=None, comments='#', names=True)
    model_dict = dict([(x[0].decode('utf-8'), (x[1], x[2])) for x in model_data])
    return model_dict

def sequence_official_poremodel(sequence, kmer_poremodel):
    k=len(kmer_poremodel.keys()[0])
    length=len(sequence)
    # check sequence length
    if length < k:
        # Assign mean and std value
        kmer_means=list()
        kmer_stdvs=list()
        [kmer_means.extend((float(90.2083),)*1) for i in range(length)]
        [kmer_stdvs.extend((float(2.0),)*1) for i in range(length)]
    else:
        # Divide sequence into kmers
        kmers = [sequence[i:i + k] for i in range(0, length - k + 1)]
        # Assign mean and std value
        kmer_means, kmer_stdvs = zip(*[kmer_poremodel[kmer] for kmer in kmers])
        kmer_means=list(kmer_means)
        kmer_stdvs=list(kmer_stdvs)
        # Append tail
        [kmer_means.extend((float(90.2083),)*1) for i in range(k-1)]
        [kmer_stdvs.extend((float(2.0),)*1) for i in range(k-1)]
    # return
    kmer_means = np.array(kmer_means)
    kmer_stdvs = np.array(kmer_stdvs)
    return kmer_means,kmer_stdvs


#----------- main program: sequence to raw signal --------------#
# default parameters: 
#     repeat_alpha=0.1
#     repeat_more=1
#     event_std=1.0
#     filter_freq=850
#     noise_std=1.5
def sequence_to_true_signal(input_part, kmer_poremodel='null', perfect=0, p_len=1,
    repeat_alpha=0.1, repeat_more=1, event_std=1.0, filter_freq=850, noise_std=1.5, 
    sigroot='signal',aliroot='align', seed=0, aliout=False):
    #--- unzip input args ---#
    sequence = input_part[0]
    seq_name = input_part[1]
    #--- get kmer signal ----#
    mean_result, std_result = sequence_official_poremodel(sequence, kmer_poremodel)
    #--- kmer simulator -----#
    if perfect:
        final_result, final_ali = repeat_k_time(p_len, mean_result)
    else:
        #-> 1. repeat N times 
        indep_result, final_ali, event_idx = repeat_n_time(repeat_alpha, mean_result, 
            repeat_more, seed)
        np.random.seed(seed)
        event_std = np.random.uniform(-1*event_std*std_result[event_idx], event_std*std_result[event_idx])
        final_result = mean_result[event_idx] + event_std
        #-> 2. low pass filter
        if filter_freq>0:
            h,h_start,N = low_pass_filter(4000.0, filter_freq, 40.0)
            final_result = np.convolve(final_result,h)[h_start+1:-(N-h_start-1)+1]
        #-> 3. add gauss noise
        if noise_std>0:
            final_result = final_result + add_noise(noise_std, len(final_result), seed=seed)
    #--- make integer -------#
    final_result = np.array(final_result)
    final_result = np.array(map(int, 5.7*final_result+14))
    #--- write to file ------#
    write_output(final_result, sigroot+'_{}.txt'.format(seq_name))
    if not arg.perfect:
        if aliout:
            write_alignment(final_ali, aliroot+'_{}.ali'.format(seq_name))


#=================== main =======================#
if __name__ == '__main__':

    #--------- argument part -------------#
    parser = argparse.ArgumentParser(description='convert the \
        input sequence to nanopore signal')
    parser.add_argument('-i', action='store', dest='input', required=True, 
        help='the input file')
    parser.add_argument('-p', action='store', dest='output', required=True,
        help='prefix the output file')
    parser.add_argument('-l', action='store', dest='alignment', required=True,
        help='prefix the alignment file')
    parser.add_argument('-m', action='store', dest='poremodel', required=True,
        help='official kmer pore model')
    parser.add_argument('-t', action='store', dest='threads',
        type=int, help='the number of threads used. (default is 1)', default=1)
    parser.add_argument('-a', action='store', dest='alpha',
        type=float, help='change the distribution of the signal repeat time, \
        value between 0 and 1, 0.1 (default) would give the distribution best \
        simulate the real case, 0 would give distribution whose basecalling \
        result is slightly worse than the real case, 1 would give the almost \
        perfect basecalling result using Albacore', default=0.1)
    parser.add_argument('-u', action='store', dest='more',
        type=int, help='tune sampling rate to around 8. (default is 1)', default=1)
    parser.add_argument('-e', action='store', dest='event_std',
        type=float, help='set the std of the event. \
        The higher the value, the more variable the event. (default is 1.0)',
        default=1.0)
    parser.add_argument('-f', action='store', dest='filter_freq',
        type=float, help='change the cut frequency in the low pass filter. \
        The higher the value, the smoother the signal. (default is 850) \
        Set -1 to disable',
        default=850)
    parser.add_argument('-s', action='store', dest='noise_std',
        type=float, help='set the std of the noise. \
        The higher the value, the blurred the signal. (default is 1.5)',
        default=1.5)
    parser.add_argument('-S', action='store', dest='seed', type=int, default=0,
        help='the random seed, for reproducibility')
    parser.add_argument('--perfect', action='store', dest='perfect',
        type=bool, help='Do you want a perfect signal and sequence',
        default=False)
    parser.add_argument('--perflen', action='store', dest='perflen',
        type=int, help='repeat length for perfect mode',
        default=1)
    parser.add_argument('--outali', action='store', dest='outali',
        type=bool, help='Do you want to output the ground-truth alignment',
        default=False)


    #---------- input list ---------------#
    arg = parser.parse_args()
    seq_list = get_seq_list(arg.input)
    id_list = get_id_list(arg.input)
    in_list = zip(seq_list, id_list)

    #---------- load pore model ----------#
    kmer_poremodel=load_official_poremodel(arg.poremodel)

    #---------- partial function ---------#
    func=partial(sequence_to_true_signal, \
        kmer_poremodel=kmer_poremodel, perfect=arg.perfect, p_len=arg.perflen, \
        event_std=arg.event_std, filter_freq=arg.filter_freq, noise_std=arg.noise_std, \
        repeat_alpha=arg.alpha, repeat_more=arg.more, sigroot=arg.output, 
        aliroot=arg.alignment, seed=arg.seed, aliout=arg.outali)

    #---------- multi process ------------#
    p = Pool(arg.threads)
    list(tqdm(p.imap(func, in_list),total=len(in_list)))
    p.close()
    p.join()

