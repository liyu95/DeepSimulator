import h5py
import numpy as np
import sys
import os
import uuid
from shutil import copyfile
import argparse
from os.path import basename
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Generate a new fasta5 file')
parser.add_argument('-i', action='store', dest='fast5_fn', required=True, 
    help='the template fasta5 file')
parser.add_argument('-s', action='store', dest='signal_for_mod', required=True,
    help='the input signal')
parser.add_argument('-t', action='store', dest='threads',
    type=int, help='the number of threads used. (default is 1)', default=1)
parser.add_argument('-d', action='store', dest='dest', default='./',
    help='the store directory')

result=parser.parse_args()


#-> input fast5 file
fast5_fn = result.fast5_fn
signal_dir_for_mod = result.signal_for_mod
directory = result.dest

def mod_raw_signal(fast5_fn, data_in, uid):
    ##Open file
    try:
        fast5_data = h5py.File(fast5_fn, 'r+')
    except IOError:
        raise IOError, 'Error opening file. Likely a corrupted file.'

    #Get raw data
    try:
        raw_dat   = fast5_data['/Raw/Reads/'].values()[0]
        raw_attrs = raw_dat.attrs
        del raw_dat['Signal']
        raw_dat.create_dataset('Signal',data=data_in, dtype='i2', compression='gzip', compression_opts=9)  #-> with compression
        raw_attrs['duration'] = data_in.size
        raw_attrs['read_id'] = uid
    except:
        raise RuntimeError, (
            'Raw data is not stored in Raw/Reads/Read_[read#] so ' +
            'new segments cannot be identified.')
    fast5_data.close()

def create_fast5(signal_for_mod):
    # The new read id and the file name
    uid = str(uuid.uuid4())

    file = os.path.join(directory, 
        basename(signal_for_mod).split('.')[0]+'_'+uid+'.fast5')

    #-> get signal data for mod
    signal = np.loadtxt(signal_for_mod).T

    copyfile(fast5_fn, file)

    #-> modify signal data inside fast5
    mod_raw_signal(file, signal, uid)

if __name__ == '__main__':
    if fast5_fn==None or signal_dir_for_mod==None:
        sys.exit('Please provide the template fast5 and the signal')

    file_list = os.listdir(signal_dir_for_mod)
    file_list = map(lambda x: os.path.join(signal_dir_for_mod, x),
        file_list)
    p = Pool(result.threads)
    p.map(create_fast5, file_list)








