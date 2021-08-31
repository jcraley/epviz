import numpy as np
from preprocessing.eeg_info import EegInfo


def _check_label(label, label_list):
    """
    Checks if a label is in the label list
    """
    label_CAPS = {k.upper(): v for k, v in label_list.items()}
    ret = _check_label_helper(label, label_CAPS)
    if ret == -1:
        labels_noEEG = {}
        labels_noRef = {}
        for k,v in label_CAPS.items():
            loc = k.find("EEG ")
            if loc != -1:
                k2 = k[loc+4:]
                labels_noEEG[k2] = label_CAPS[k]
            else:
                labels_noEEG[k] = label_CAPS[k]
        ret = _check_label_helper(label, labels_noEEG)
        if ret == -1:
            for k,v in labels_noEEG.items():
                loc = k.find("-REF")
                if loc != -1:
                    k2 = k[0:loc]
                    labels_noRef[k2] = labels_noEEG[k]
                else:
                    labels_noRef[k] = labels_noEEG[k]
            ret = _check_label_helper(label, labels_noRef)
            if ret == -1:
                label2 = ""
                if label == "T7":
                    label2 = "T3"
                if label == "P7":
                    label2 = "T5"
                if label == "T8":
                    label2 = "T4"
                if label == "P8":
                    label2 = "T6"
                ret = _check_label_helper(label2, label_CAPS)
                if ret == -1:
                    ret = _check_label_helper(label2, labels_noEEG)
                    if ret == -1:
                        ret = _check_label_helper(label2, labels_noRef)
    return ret

def _check_label_helper(label, label_list):
    if label in label_list:
        return label_list[label]
    return -1

def _check_montage(label, label_list):
    """
    Checks if we are in ref montage or normal montage
    returns:
        0 for normal, 1 for ref
    """
    ret = 1
    for i in range(len(label_list)):
        if label.upper().find(label_list[i]) != -1:
            ret = 0
    return ret


class EdfMontage():
    """ A class for loading info and buffers from EDF files """

    def __init__(self, eeg_info):
        self.montage_data = []
        self.labels = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                       "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                       "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        self.labelsAR = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                        "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        self.eeg_info = eeg_info
        self.nchns = self.eeg_info.nchns


    def reorder_data(self, data):
        """
        Reorder data so that it is in the proper montage format

        inputs:
            data - buffer of data loaded from .edf file

        returns:
            montage_data - a EdfMontage object with the correctly ordered channels
            idx_0 - the index of the first channel to get the fs in the main window
        """
        mont = _check_montage(list(self.eeg_info.labels2chns.keys())[0],self.labels)
        if mont == 1:
            self.nchns = 19
            self.montage_data = self.ar(data)
        else:
            self.nchns = 18
            self.montage_data = np.zeros((self.nchns, data.shape[1]))
            for chn in range(len(self.labels)):
                edf_chn = _check_label(self.labels[chn],self.eeg_info.labels2chns)
                if edf_chn != -1:
                    self.montage_data[chn,:] = data[edf_chn,:]
        return self.montage_data

    def ar(self, data):
        """
        Make average reference montage

        inputs:
            data - buffer of signals
        outputs:
            the montage
        """
        montage_ar= np.zeros((self.nchns, data.shape[1]))
        for chn in range(len(self.labelsAR)):
            edf_chn = _check_label(self.labelsAR[chn],self.eeg_info.labels2chns)
            if edf_chn != -1:
                montage_ar[chn,:] = data[edf_chn,:]
        return montage_ar

    def get_bipolar_from_ar(self,ar_data):
        """
        Produces bipolar data from average reference
        """
        montage_bip = np.zeros((18,ar_data.shape[1]))
        bip_idx = np.zeros((18,2))
        for k in range(18):
            str0 = self.labels[k].split('-')[0]
            str1 = self.labels[k].split('-')[1]
            idx0 = np.argmax(np.char.find(self.labelsAR,str0))
            idx1 = np.argmax(np.char.find(self.labelsAR,str1))
            bip_idx[k,0] = idx0
            bip_idx[k,1] = idx1
        for k in range(18):
            idx0 = bip_idx[k,0]
            idx1 = bip_idx[k,1]
            montage_bip[k,:] = ar_data[int(idx0),:] - ar_data[int(idx1),:]
        return montage_bip

    def getIndexForFs(self, label_names):
        idx = 0
        for i in range(len(self.labelsAR)):
            for k, v in label_names.items():
                if k.find(self.labelsAR[i]) != -1:
                    idx = v
        return idx

    def get_predictions(self, data, pi, max_time, fs):
        """
        Loads in predictions if they were previously saved.

        params:
            data - the edf data
            pi - the prediction info object which will hold the predictions
        returns:
            1 if predictions are found, 0 otherwise
        """
        if "PREDICTIONS" in self.eeg_info.labels2chns:
            pred_chn = self.eeg_info.labels2chns["PREDICTIONS"]
            pi.preds = data[pred_chn]
            pi.preds = np.array(pi.preds)
            pi.preds_to_plot = pi.preds
            pi.preds_loaded = 1
            pi.pred_width = (fs * max_time) / pi.preds.shape[0]
            return 1
        elif "PREDICTIONS_0" in self.eeg_info.labels2chns:
            i = 0
            pi.preds = []
            while "PREDICTIONS_" + str(i) in self.eeg_info.labels2chns:
                pred_chn = self.eeg_info.labels2chns["PREDICTIONS_" + str(i)]
                pi.preds.append(data[pred_chn])
                i += 1
            pi.preds = np.array(pi.preds)
            pi.preds = pi.preds.T
            pi.preds_to_plot = pi.preds
            pi.preds_loaded = 1
            pi.pred_by_chn = 1
            pi.pred_width = (fs * max_time) / pi.preds.shape[0]
            return 1
        return 0
