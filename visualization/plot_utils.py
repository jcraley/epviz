""" Utility functions for plot.py """
from copy import deepcopy
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from preprocessing import dsp

def check_annotations(t_start, window_size, edf_info):
    """ Checks to see if there are any anotations in the range t_start to t_end sec

    Args:
        t_start - start time for a graph
        window_size - the number of seconds being plotted at a time
        edf_info - edf_info object containing annotations

    Returns:
        ret - an array that is filled with any annotations[t_start:t_end]
        idx_w_ann - an array of size window_size that tells whether or not there is
                    an adjacent annotation
    """

    ann = edf_info.annotations
    t_end = t_start + window_size - 1
    i = 0
    ret = []
    idx_w_ann = np.zeros((window_size))

    if len(ann[0]) != 0:
        ann_i = int(float(ann[0,i]))
        while ann_i <= t_end and i < ann.shape[1]:
            if int(float(ann[0,i])) >= t_start and int(float(ann[0,i])) <= t_end:
                ret.append(ann[:,i])
                idx_w_ann[int(float(ann[0,i]))-t_start] = 1
                i += 1
            elif int(float(ann[0,i])) <= t_end:
                i += 1
            else:
                i = ann.shape[1]
    else:
        return ret, idx_w_ann

    if window_size > 1:
        if not(idx_w_ann[0] == 1 and idx_w_ann[1] == 1):
            idx_w_ann[0] = 0
        i = 1
        while i < window_size - 1:
            if not((idx_w_ann[i-1] == 1 or idx_w_ann[i+1] == 1) and idx_w_ann[i] == 1):
                idx_w_ann[i] = 0
            i += 1
        if idx_w_ann[window_size - 2] == 0 and idx_w_ann[window_size - 1] == 1:
            idx_w_ann[window_size - 1] = 0

    return ret, idx_w_ann

def filter_data(data, fs, fi, show=1):
    """ Filters the data.
        Progress bar is created if the process is estimated to take > 4s

    Args:
        data - the data to filter
        fs - the fs
        fi - a filterInfo object
        show - can be set to 0 for testing purposes so as not to show the
            filtering progress bar
    Returns:
        filtered data
    """
    lp = fi.lp
    hp = fi.hp
    bp1 = fi.bp1
    bp2 = fi.bp2
    notch = fi.notch
    if fi.do_lp == 0 or lp < 0 or lp > fs / 2:
        lp = 0
    if fi.do_hp == 0 or hp < 0 or hp > fs / 2:
        hp = 0
    if fi.do_bp == 0 or bp1 < 0 or bp1 > fs / 2 or bp2 < 0 or bp1 > fs / 2 or bp2 - bp1 <= 0:
        bp1 = 0
        bp2 = 0
    if fi.do_notch == 0 or fi.notch < 0 or fi.notch > fs / 2:
        notch = 0

    nchns = len(data)
    filt_bufs = deepcopy(data)

    if show:
        progress = QProgressDialog("Filtering...", "Cancel", 0, nchns * 4)
        progress.setWindowModality(Qt.WindowModal)

    i = 0
    for chn in range(nchns):
        # Notch
        if notch > 0:
            filt_bufs[chn] = dsp.apply_notch(filt_bufs[chn], fs, fi.notch)
        i += 1
        if show:
            progress.setValue(i)
            if progress.wasCanceled():
                fi.filter_canceled = 1
                break
        # LPF
        if lp > 0:
            filt_bufs[chn] = dsp.apply_low_pass(filt_bufs[chn], fs, lp)
        i += 1
        if show:
            progress.setValue(i)
            if progress.wasCanceled():
                fi.filter_canceled = 1
                break
        # HPF
        if hp > 0:
            filt_bufs[chn] = dsp.apply_high_pass(filt_bufs[chn], fs, hp)
        i += 1
        if show:
            progress.setValue(i)
            if progress.wasCanceled():
                fi.filter_canceled = 1
                break
        # BPF
        if bp1 > 0:
            filt_bufs[chn] = dsp.apply_band_pass(filt_bufs[chn], fs, [bp1, bp2])
        i += 1
        if show:
            progress.setValue(i)
            if progress.wasCanceled():
                fi.filter_canceled = 1
                break

    return filt_bufs

def convert_from_count(count):
    """ Converts time from count (int in seconds) to the time format
        hh:mm:ss.

    Args:
        count - the value of count
    Returns:
        hrs, min, sec - the time
    """
    t = count
    hrs = 0
    minutes = 0
    sec = 0
    if int(t / 3600) > 0:
        hrs = int(t / 3600)
        t = t % 3600
    if int(t / 60) > 0:
        minutes = int(t / 60)
        t = t % 60
    sec = t
    return hrs, minutes, sec

def get_time(count):
    """ Creates a string for the time in seconds.

    Args:
        count - the current value of the plot in seconds
    Returns:
        t_str - a string of the seconds in the form hrs:min:sec
    """
    t_str = ""
    hrs, minutes, sec = convert_from_count(count)
    if sec >= 10:
        str_sec = str(sec)
    else:
        str_sec = "0" + str(sec)
    if minutes >= 10:
        str_min = str(minutes)
    else:
        str_min = "0" + str(minutes)
    str_hr = str(hrs)
    t_str = str_hr + ":" + str_min + ":" + str_sec
    return t_str
