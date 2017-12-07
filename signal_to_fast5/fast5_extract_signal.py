import h5py
import numpy as np
import sys
import os


def get_raw_signal(fast5_fn):
    ##Open file
    try:
        fast5_data = h5py.File(fast5_fn, 'r')
    except IOError:
        raise IOError, 'Error opening file. Likely a corrupted file.'

    #Get raw data
    try:
        raw_dat   = fast5_data['/Raw/Reads/'].values()[0]
        raw_attrs = raw_dat.attrs
        raw_dat = raw_dat['Signal'].value
    except:
        raise RuntimeError, (
            'Raw data is not stored in Raw/Reads/Read_[read#] so ' +
            'new segments cannot be identified.')
    fast5_data.close()

    return (raw_dat)


if __name__ == '__main__':

    #------- main -------#
    if len(sys.argv) < 2:
        print 'python extract_signal.py <input_fast5> <raw_signal_outfile> '
        sys.exit(-1)

    #-> input fast5 file
    fast5_fn = sys.argv[1]
    raw_signal_out = sys.argv[2]

    #-> get raw data
    raw_signal = get_raw_signal(fast5_fn)

    #----- WS Output Raw_Data and Genome_Label -----#
    np.savetxt(raw_signal_out, raw_signal, fmt='%d')

