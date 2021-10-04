""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from visualization.spectrogram_window.spec_options import SpecOptions
from visualization.spectrogram_window.spec_info import SpecInfo
from visualization.plot import MainPage
from visualization.plot import check_args, get_args
from unittest.mock import patch

app = QApplication([])
class TestFilter(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/E_B_1-DeID_0003.edf"
        patch('sys.argv', ["--show","0"])
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        self.parent.edf_info = SpecInfo()
        self.parent.edf_info.fs = 256
        self.spec_info = SpecInfo()
        self.ui3 = SpecOptions(self.spec_info, self.parent)
        self._load_signals()
        self.ui = SpecOptions(self.spec_info, self.parent)

    def test_setup(self):
        # Test that channels are loaded properly at startup
        lbls = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        self.assertEqual(lbls.sort(), self.ui.labels_flipped.sort())

    def test_clear_spec(self):
        # reset the channels
        self.ui.chn_combobox.setCurrentIndex(5)
        self.spec_info.chn_plotted = 5
        self.ui.clear_spec()
        self.assertEqual(self.ui.chn_combobox.currentIndex(), 0)
        self.assertEqual(self.spec_info.chn_plotted, -1)

    def test_close_window_no_chn(self):
        # Try closing the window with no channel selected
        self.assertEqual(self.spec_info.min_fs, 1)
        self.assertEqual(self.spec_info.max_fs, 30)
        self.ui.btn_get_max_fs.setValue(28)
        self.ui.btn_get_min_fs.setValue(3)
        self.ui.check()
        self.assertEqual(self.spec_info.plot_spec, 0)
        self.assertEqual(self.spec_info.min_fs, 3)
        self.assertEqual(self.spec_info.max_fs, 28)


    def test_close_window_chn0(self):
        # Try closing the window with a channel selected
        self.ui.btn_get_max_fs.setValue(28)
        self.ui.btn_get_min_fs.setValue(3)
        self.ui.chn_combobox.setCurrentIndex(3)
        self.ui.check()
        self.assertEqual(self.spec_info.plot_spec, 1)
        self.assertEqual(self.spec_info.min_fs, 3)
        self.assertEqual(self.spec_info.max_fs, 28)
        self.assertEqual(self.spec_info.chn_name, 'T7-P7')

        self.ui2 = SpecOptions(self.spec_info, self.parent)
        self.ui2.chn_combobox.setCurrentIndex(0)
        self.ui2.check()
        self.assertEqual(self.spec_info.plot_spec, 0)
        self.assertEqual(self.spec_info.chn_plotted, -1)

    def test_close_window_chn1(self):
        # Try closing the window with a channel selected
        self.ui.chn_combobox.setCurrentIndex(3)
        self.ui.check()

        self.ui2 = SpecOptions(self.spec_info, self.parent)
        self.ui2.chn_combobox.setCurrentIndex(6)
        self.parent.filter_checked = 1
        self.ui2.check()
        self.assertEqual(self.spec_info.plot_spec, 1)

        self.ui4 = SpecOptions(self.spec_info, self.parent)
        self.ui4.chn_combobox.setCurrentIndex(0)
        self.assertEqual(self.spec_info.min_fs, 1)
        self.assertEqual(self.spec_info.max_fs, 30)
        # set these to bad values, should not get updated
        # and an error should not be thrown since no plotting will happen
        self.ui4.btn_get_max_fs.setValue(1)
        self.ui4.btn_get_min_fs.setValue(27)
        self.ui4.check()
        self.assertEqual(self.spec_info.plot_spec, 0)
        self.assertEqual(self.spec_info.min_fs, 1)
        self.assertEqual(self.spec_info.max_fs, 30)

    def _load_signals(self):
        # for loading in the test file
        self.parent.argv.show = 0
        self.parent.argv.fn = self.TEST_FN
        self.parent.load_data(name=self.TEST_FN)
        self.parent.chn_ops.cbox_bip.setChecked(1)
        self.parent.chn_ops.check()
        self.parent.call_initial_move_plot()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)