""" Module for various filtering operations """
import scipy.signal

def apply_low_pass(x, fs, fc=30, N=4):
    """ Apply a low-pass filter to the signal
    """
    wc = fc / (fs / 2)
    b, a = scipy.signal.butter(N, wc)
    return scipy.signal.filtfilt(b, a, x, method='gust')

def apply_high_pass(x, fs, fc=1.6, N=4):
    """ Apply a high-pass filter to the signal
    """
    wc = fc / (fs / 2)
    b, a = scipy.signal.butter(N, wc, btype='highpass')
    return scipy.signal.filtfilt(b, a, x, method='gust')

def apply_notch(x, fs, fc=60, Q=20.0):
    """ Apply a notch filter at fc Hz
    """
    w60Hz = fc / (fs / 2)
    b, a = scipy.signal.iirnotch(w60Hz, Q)
    return scipy.signal.filtfilt(b, a, x, method='gust')

def apply_band_pass(x, fs, fc=[1.6,30], N=4):
    """ Apply a low-pass filter to the signal
    """
    wc = fc / (fs / 2)
    b, a = scipy.signal.butter(N, wc, btype='bandpass')
    return scipy.signal.filtfilt(b, a, x, method='gust')
