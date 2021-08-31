from collections import defaultdict
from copy import deepcopy

import numpy as np
import scipy.signal
from numpy.fft import fft, fftfreq
from scipy.special import comb as nchoosek
from scipy.stats import norm
from scipy.stats.stats import pearsonr
from sklearn.preprocessing import StandardScaler, scale
from scipy.signal import resample_poly


#################
# PREPROCESSING #
#################
def applyNotch60(x, fs, Q=20.0):
    """Apply a notch filter at 60 Hz
    """
    w60Hz = 60 / (fs / 2)
    b, a = scipy.signal.iirnotch(w60Hz, Q)
    return scipy.signal.filtfilt(b, a, x, method='gust')


def applyLowPass(x, fs, fc=30, N=4):
    """Apply a low-pass filter to the signal
    """
    wc = fc / (fs / 2)
    b, a = scipy.signal.butter(N, wc)
    return scipy.signal.filtfilt(b, a, x, method='gust')


def applyHighPass(x, fs, fc=1.6, N=4):
    """Apply a high-pass filter to the signal
    """
    wc = fc / (fs / 2)
    b, a = scipy.signal.butter(N, wc, btype='highpass')
    return scipy.signal.filtfilt(b, a, x, method='gust')


def clip(x, clip_level):
    """Clip the signal to a given standard deviation"""
    mean = np.mean(x)
    std = np.std(x)
    return np.clip(x, mean - clip_level * std, mean + clip_level * std)


def prefilter(bufs, fs, notch=False, lpf_fc=0, hpf_fc=0, clip_level=3.0,
              standardize=False):
    """Apply 60 Hz notch filter and lowpass filter

    inputs:
        bufs - list of buffers to be processed
        fs - list of sampling frequencies
        notch - apply a notch filter at 60 Hz (bool)
        lpf_fc - lpf cutoff, 0 for none
        hpf_fc - hpf cutoff, 0 for none
        clip_level - clip recordings at std level, 0 for none
        standardize - scale channel to mean 0, std 1

    returns:
        filt_bufs: filtered buffers
    """
    nchns = len(bufs)
    filt_bufs = deepcopy(bufs)
    for chn in range(nchns):
        # Notch
        if notch:
            filt_bufs[chn] = applyNotch60(filt_bufs[chn], fs)
        # LPF
        if lpf_fc > 0:
            filt_bufs[chn] = applyLowPass(filt_bufs[chn], fs, lpf_fc)
        # HPF
        if hpf_fc > 0:
            filt_bufs[chn] = applyHighPass(filt_bufs[chn], fs, hpf_fc)
        if clip_level > 0:
            filt_bufs[chn] = clip(filt_bufs[chn], clip_level)
        # Standardize
        if standardize:
            filt_bufs[chn] = scale(filt_bufs[chn])

    return filt_bufs


def resample_256to200(bufs):
    """Resample all the buffers from 256 Hz to 200 Hz
    """
    for ii in range(len(bufs)):
        bufs[ii] = resample_poly(bufs[ii], up=25, down=32, axis=0)
    return bufs
