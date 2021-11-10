""" Module for testing the edf loader """
import sys
import numpy as np
sys.path.append('visualization')
import unittest
from visualization.preprocessing.edf_loader import EdfLoader, _check_label
from visualization.preprocessing.eeg_info import EegInfo
import pyedflib

class TestEdfLoading(unittest.TestCase):
    def setUp(self):
        # Setup
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/test_files/chb01_03.edf"
        self.edf_loader = EdfLoader()

    def test_setup(self):
        pass

    def test_check_label(self):
        # Test checking labels
        #label_list = {"FP1": 0, "CZ": 1, ""}
        #_check_label()
        pass

    def test_load_metadata0(self):
        # Test loading edf file metadata
        label_list = ['FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1', 'FP1-F3', 'F3-C3',
                      'C3-P3', 'P3-O1', 'FP2-F4', 'F4-C4', 'C4-P4', 'P4-O2',
                      'FP2-F8', 'F8-T8', 'T8-P8', 'P8-O2', 'FZ-CZ', 'CZ-PZ',
                      'P7-T7', 'T7-FT9', 'FT9-FT10', 'FT10-T8', 'T8-P8']
        labels2chns = {'FP1-F7': 0, 'F7-T7': 1, 'T7-P7': 2, 'P7-O1': 3,
                       'FP1-F3': 4, 'F3-C3': 5, 'C3-P3': 6, 'P3-O1': 7,
                       'FP2-F4': 8, 'F4-C4': 9, 'C4-P4': 10, 'P4-O2': 11,
                       'FP2-F8': 12, 'F8-T8': 13, 'T8-P8': 22, 'P8-O2': 15,
                       'FZ-CZ': 16, 'CZ-PZ': 17, 'P7-T7': 18, 'T7-FT9': 19,
                       'FT9-FT10': 20, 'FT10-T8': 21}
        chns2labels = {0: 'FP1-F7', 1: 'F7-T7', 2: 'T7-P7', 3: 'P7-O1',
                       4: 'FP1-F3', 5: 'F3-C3', 6: 'C3-P3', 7: 'P3-O1',
                       8: 'FP2-F4', 9: 'F4-C4', 10: 'C4-P4', 11: 'P4-O2',
                       12: 'FP2-F8', 13: 'F8-T8', 14: 'T8-P8', 15: 'P8-O2',
                       16: 'FZ-CZ', 17: 'CZ-PZ', 18: 'P7-T7', 19: 'T7-FT9',
                       20: 'FT9-FT10', 21: 'FT10-T8', 22: 'T8-P8'}
        self.edf_info = self.edf_loader.load_metadata(self.TEST_FN)
        self.assertEqual(self.edf_info.edf_fn, self.TEST_FN)
        self.assertEqual(self.edf_info.name, self.TEST_FN.split('/')[-1].split('.')[0])
        self.assertEqual(self.edf_info.file_duration, 3600)
        for x in self.edf_info.nsamples:
            self.assertEqual(x, 921600)
        self.assertEqual(len(self.edf_info.nsamples), 23)
        self.assertEqual(self.edf_info.nchns, 23)
        self.assertEqual(self.edf_info.fs, 256)
        self.assertEqual(self.edf_info.label_list, label_list)
        for x in self.edf_info.annotations:
            self.assertEqual(len(x), 0)
        self.assertEqual(len(self.edf_info.annotations), 3)
        self.assertEqual(self.edf_info.labels2chns, labels2chns)
        self.assertEqual(self.edf_info.chns2labels, chns2labels)

    def test_load_metadata1(self):
        # Test loading edf file metadata with label_list set
        label_list = ['FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1']
        self.edf_loader.label_list = label_list
        labels2chns = {'FP1-F7': 0, 'F7-T7': 1, 'T7-P7': 2, 'P7-O1': 3}
        chns2labels = {0: 'FP1-F7', 1: 'F7-T7', 2: 'T7-P7', 3: 'P7-O1'}
        self.edf_info = self.edf_loader.load_metadata(self.TEST_FN)
        self.assertEqual(self.edf_info.edf_fn, self.TEST_FN)
        self.assertEqual(self.edf_info.name, self.TEST_FN.split('/')[-1].split('.')[0])
        self.assertEqual(self.edf_info.file_duration, 3600)
        for x in self.edf_info.nsamples:
            self.assertEqual(x, 921600)
        self.assertEqual(len(self.edf_info.nsamples), 4)
        self.assertEqual(self.edf_info.nchns, 4)
        self.assertEqual(self.edf_info.fs, 256)
        self.assertEqual(self.edf_info.label_list, label_list)
        for x in self.edf_info.annotations:
            self.assertEqual(len(x), 0)
        self.assertEqual(len(self.edf_info.annotations), 3)
        self.assertEqual(self.edf_info.labels2chns, labels2chns)
        self.assertEqual(self.edf_info.chns2labels, chns2labels)

    def test_check_label(self):
        # Test _check_label
        label_list = ['FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1', "FP2"]
        self.assertEqual(_check_label("abc", label_list), "")
        self.assertEqual(_check_label("fp1", label_list), "")
        self.assertEqual(_check_label("fp2", label_list), "FP2")
        self.assertEqual(_check_label("fp2-f4", label_list), "")
        self.assertEqual(_check_label('F7-T7', label_list), 'F7-T7')

    def test_load_buffers(self):
        # Test loading buffers
        label_list = ['FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1']
        self.edf_loader.label_list = label_list
        self.edf_info = self.edf_loader.load_metadata(self.TEST_FN)
        bufs = self.edf_loader.load_buffers(self.edf_info)
        f = pyedflib.EdfReader(self.edf_info.edf_fn)
        bufs_corr = []
        for i in range(len(label_list)):
            bufs_corr.append(f.readSignal(i))
        for x, xx in zip(bufs, bufs_corr):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
