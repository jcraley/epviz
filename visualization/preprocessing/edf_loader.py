""" Module for loading edf files """
import pyedflib

from visualization.preprocessing.eeg_info import EegInfo


def _check_label(label, label_list):
    """
    Checks if a label is in the label list
    """
    # If the label is not present, try splitting it
    if label.upper() not in label_list:
        label = label[4:].split('-')[0].upper()
    # If the label is present, load the channel
    if label.upper() in label_list:
        return label.upper()
    return False


class EdfLoader():
    """ A class for loading info and buffers from EDF files """

    def __init__(self, label_list=None):
        self.label_list = label_list

    def load_metadata(self, fn):
        """
        Load the information from the edf file

        inputs:
            fn - name of .edf file

        returns:
            edf_info - an EdfInfo object populated with the edfs info
        """
        # Initialize eeg_info
        eeg_info = EegInfo()
        eeg_info.edf_fn = fn
        eeg_info.name = fn.split('/')[-1].split('.')[0]
        eeg_info.label_list = self.label_list

        # Load the metadata
        f = pyedflib.EdfReader(fn)
        nsignals = f.signals_in_file
        signal_labels = f.getSignalLabels()
        nsamples = f.getNSamples()
        sample_frequencies = f.getSampleFrequencies()
        eeg_info.file_duration = f.getFileDuration()
        eeg_info.annotations = f.readAnnotations()

        # If a label list is provided, load info for the channels
        if self.label_list:
            eeg_info.nchns = len(self.label_list)
            eeg_info.nsamples = [0] * eeg_info.nchns
            eeg_info.fs = [0] * eeg_info.nchns
            # Create the mappings from labels to channels based on label_list
            eeg_info.labels2chns = {}
            eeg_info.chns2labels = {}
            for chn, label in enumerate(self.label_list):
                eeg_info.labels2chns[label] = chn
                eeg_info.chns2labels[chn] = label
            # Load info from relevant channels
            for edf_chn in range(nsignals):
                curr_label = _check_label(signal_labels[edf_chn],
                                          self.label_list)
                if curr_label:
                    chn = eeg_info.labels2chns[curr_label]
                    eeg_info.nsamples[chn] = nsamples[edf_chn]
                    eeg_info.fs[chn] = sample_frequencies[edf_chn]

        # If no label list is provided, load all metadata
        else:
            eeg_info.nsamples = nsamples
            eeg_info.fs = sample_frequencies
            eeg_info.labels2chns = {}
            eeg_info.chns2labels = {}
            eeg_info.nchns = nsignals
            eeg_info.label_list = []
            for edf_chn in range(nsignals):
                label = signal_labels[edf_chn]
                eeg_info.label_list.append(label.upper())
                eeg_info.labels2chns[label.upper()] = edf_chn
                eeg_info.chns2labels[edf_chn] = label.upper()
        # Close the edf file
        f._close()
        del f

        if len(set(eeg_info.fs)) == 1:
            eeg_info.fs = eeg_info.fs[0]

        return eeg_info

    def load_buffers(self, eeg_info):
        """
        Load the information from the edf file

        inputs:
            eeg_info - info for eeg file to load

        returns:
            bufs - list of channel buffers from the EDF file
        """
        bufs = [0] * eeg_info.nchns

        f = pyedflib.EdfReader(eeg_info.edf_fn)
        nsignals = f.signals_in_file
        signal_labels = f.getSignalLabels()
        # Loop over the signals in the edf file
        for edf_chn in range(nsignals):
            # Check the label and load
            curr_label = _check_label(signal_labels[edf_chn],
                                      eeg_info.label_list)
            if curr_label:
                chn = eeg_info.labels2chns[curr_label]
                bufs[chn] = f.readSignal(edf_chn)
        return bufs
