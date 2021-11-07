""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
from PyQt5.QtWidgets import QApplication
import unittest
from visualization.plot_utils import *
from preprocessing.edf_loader import EdfLoader
from visualization.filtering.filter_info import FilterInfo
import pyedflib
import numpy as np
import visualization.preprocessing.dsp as dsp

app = QApplication([])
class TestPlotUtils(unittest.TestCase):
    """
    def setUp(self):
        # Set the test files
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/test_file_annotations.edf"
        loader = EdfLoader()
        self.EDF_INFO = loader.load_metadata(self.TEST_FN)

    # 0. Check annotations
    def test_check_annotations(self):
        # Test check annotations
        self.EDF_INFO.annotations = np.array(self.EDF_INFO.annotations)
        ret, idx_w_ann = check_annotations(0, 10, self.EDF_INFO)
        self.assertEqual(len(ret), 3)
        self.assertEqual(len(idx_w_ann), 10)
        for x, y in zip(ret[0], self.EDF_INFO.annotations[:,0]):
            self.assertEqual(x, y)
        for x, y in zip(ret[1], self.EDF_INFO.annotations[:,1]):
            self.assertEqual(x, y)
        ret, idx_w_ann = check_annotations(532, 10, self.EDF_INFO)
        self.assertEqual(len(ret), 0)
        self.assertEqual(len(idx_w_ann), 10)
        test_edf = self.EDF_INFO
        test_edf.annotations = [[], [], []]
        ret, idx_w_ann = check_annotations(532, 10, test_edf)
        self.assertEqual(ret, [])
        self.assertEqual(len(idx_w_ann), 10)

        test_edf.annotations = np.array([[2, 3, 9], [-1, -1, -1], ["test2", "test3", "test9"]])
        ret, idx_w_ann = check_annotations(0, 10, test_edf)
        self.assertEqual(len(ret), 3)
        self.assertEqual(len(idx_w_ann), 10)
        for i in range(10):
            if i != 2 and i != 3:
                self.assertEqual(idx_w_ann[i], 0)
            else:
                self.assertEqual(idx_w_ann[i], 1)

    # 1. Filter data
    def test_filter_data(self):
        # Test filtering with different parameters
        thresh = 0.000001
        self.filter_info = FilterInfo()
        self.filter_info.fs = self.EDF_INFO.fs
        f = pyedflib.EdfReader(self.TEST_FN)
        test_data = f.readSignal(0)
        test_data = test_data[np.newaxis, ...]
        filt_bufs = np.zeros((1, test_data.shape[1]))
        filt_bufs[0, :] = dsp.apply_low_pass(test_data[0], self.EDF_INFO.fs, self.filter_info.lp)
        filt_bufs[0, :] = dsp.apply_high_pass(filt_bufs[0], self.EDF_INFO.fs, self.filter_info.hp)
        ret = filter_data(test_data, self.EDF_INFO.fs, self.filter_info)
        for x, y in zip(ret[0, :], filt_bufs[0, :]):
            self.assertTrue(abs(x - y) < thresh)
        
        # Test bandpass and notch
        self.filter_info.do_lp = 0
        self.filter_info.do_hp = 0
        self.filter_info.do_bp = 1
        self.filter_info.do_notch = 1
        self.filter_info.notch = 20
        self.filter_info.bp1 = 10
        self.filter_info.bp2 = 30
        filt_bufs = np.zeros((1, test_data.shape[1]))
        filt_bufs[0, :] = dsp.apply_notch(test_data[0], self.EDF_INFO.fs, self.filter_info.notch)
        filt_bufs[0, :] = dsp.apply_band_pass(filt_bufs[0], self.EDF_INFO.fs,
                                [self.filter_info.bp1, self.filter_info.bp2])
        ret = filter_data(test_data, self.EDF_INFO.fs, self.filter_info)
        for x, y in zip(ret[0, :], filt_bufs[0, :]):
            self.assertTrue(abs(x - y) < thresh)

    # 2. Convert from count
    def test_convert_from_count(self):
        # Test convert from count
        h, m, s = convert_from_count(0)
        self.assertEqual(h, 0)
        self.assertEqual(m, 0)
        self.assertEqual(s, 0)
        h, m, s = convert_from_count(72)
        self.assertEqual(h, 0)
        self.assertEqual(m, 1)
        self.assertEqual(s, 12)
        h, m, s = convert_from_count(3624)
        self.assertEqual(h, 1)
        self.assertEqual(m, 0)
        self.assertEqual(s, 24)
    
    # 3. Get time
    def test_get_time(self):
        # Test get time
        str0 = get_time(0)
        self.assertEqual(str0, "0:00:00")
        str0 = get_time(72)
        self.assertEqual(str0, "0:01:12")
        str0 = get_time(3624)
        self.assertEqual(str0, "1:00:24")
        str0 = get_time(759)
        self.assertEqual(str0, "0:12:39")


    def tearDown(self):
        pass
    """
if __name__ == '__main__':
    unittest.main(exit=False)
