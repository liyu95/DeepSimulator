import numpy as np
import scipy.stats as st
from random import *
import scipy.signal



#--------------- step 1: load input sequence ---------------#
def get_seq_list(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        lines = text.splitlines()
    seq_list = filter(lambda x: x!='', lines)
    seq_list = filter(lambda x: '>' not in x, seq_list)
    return seq_list

def get_id_list(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        lines = text.splitlines()
    lines = filter(lambda x: '>' in x, lines)
    id_list = map(lambda x: x.split('|')[0][1:], lines)
    return id_list

#------ output functions ------#
def write_output(result, file_name):
    with open(file_name, 'w') as f:
        for i in result:
            temp = str(i)+'\n'
            f.write(temp)

def write_alignment(result, file_name):
    with open(file_name, 'w') as f:
        for i in result:
            temp = str(i[0]+1)+' '+str(i[1]+1)+'\n'
            f.write(temp)


#---------- step 2: repeat length sample -----------#
def rep_rvs(size,a, more):
    a = a*5
    array_1 = np.ones(int(size*(0.075-0.015*a))).astype(int)
    samples = st.alpha.rvs(3.3928495261646932+a,
        -7.6451557771999035+(2*a), 50.873948369526737,
        size=(size-int(size*(0.075-0.015*a)))).astype(int)
    samples = np.concatenate((samples, array_1), 0)
    samples[samples<1] = 1
    samples[samples>40] = 40
    if more == 1:
        addi = np.array(abs(np.random.normal(2,1,size))).astype(int)
        samples[samples<8] += addi[samples<8]
        np.random.shuffle(samples)
        samples[samples<8] += addi[samples<8]
    return samples

def repeat_n_time(a, result, more):
    rep_times = rep_rvs(len(result), a, more)
    out = list()
    ali = list()
    pos = 0
    for i in range(len(result)):
        k = rep_times[i]
        cur = [result[i]] * k
        out.extend(cur)
        for j in range(k):
            ali.append((pos,i))
            pos = pos + 1
    event_idx = np.repeat(np.arange(len(result)), rep_times)
    return out,ali,event_idx
    
def repeat_k_time(k, result):
    out = list()
    ali = list()
    pos = 0
    for i in range(len(result)):
        cur = [result[i]] * k
        out.extend(cur)
        for j in range(k):
            ali.append((pos,i))
            pos = pos + 1
    return out,ali


#------------- step 3: low pass filter for signal simulation -----#
#-> low pass filter
#   sampling_rate = 4000.0, cut_off_freq = 1750.0, bandwidth_freq = 40.0
def low_pass_filter(sampling_rate, cut_off_freq, bandwidth_freq):
    # Read input parameter
    fS = sampling_rate  # Sampling rate.
    fL = cut_off_freq   # Cutoff frequency.
    fb = bandwidth_freq # Bandwidth frequency

    # Generate frequency bin
    b = fb / fS
    N = int(np.ceil((4 / b)))
    if not N % 2: N += 1  # Make sure that N is odd.
    n = np.arange(N)

    # Compute sinc filter.
    h = np.sinc(2 * fL / fS * (n - (N - 1) / 2.))

    # Compute Blackman window.
    w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) + \
        0.08 * np.cos(4 * np.pi * n / (N - 1))

    # Compute h and h_start
    h = h * w
    h /= np.sum(h)
    impulse = np.repeat(0., len(h))
    impulse[0] = 1.
    h_response = scipy.signal.lfilter(h, 1, impulse)
    h_start = np.argmax(h_response)

    # return
    return h,h_start,N


#---------- step 4: add Gaussian noise ----------#
def add_noise(std, l):
    noise = np.random.normal(0, std, l)
    return noise


