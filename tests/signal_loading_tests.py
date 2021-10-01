""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from visualization.signal_loading.channel_options import ChannelOptions
from visualization.signal_loading.channel_info import ChannelInfo, _check_label, convert_txt_chn_names
from visualization.plot import MainPage
from visualization.plot import check_args, get_args
from unittest.mock import patch
from preprocessing.edf_loader import EdfLoader

from PyQt5.QtWidgets import QCheckBox

app = QApplication([])
class TestChannelLoading(unittest.TestCase):
    def setUp(self):
        patch('sys.argv', ["--show","0"])
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        self.LABELS_AR1020 = ["O2","O1","PZ","CZ","FZ","T6","T5","T4","T3","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        # Set the test files
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/E_B_1-DeID_0003.edf"
        self.TEST_TXT_FILE = "/Users/daniellecurrey/Desktop/gui_edf_files/uw_chns_valid.txt"
        self.TEST_INVALID_TXT_FILE = "/Users/daniellecurrey/Desktop/gui_edf_files/uw_chns_invalid.txt"
        # Load in the file
        loader = EdfLoader()
        self.parent.edf_info_temp = loader.load_metadata(self.TEST_FN)
        # Create the ChannelInfo object
        self.channel_info = ChannelInfo()
        self.channel_info.chns2labels = self.parent.edf_info_temp.chns2labels
        self.channel_info.labels2chns = self.parent.edf_info_temp.labels2chns
        self.channel_info.fs = self.parent.edf_info_temp.fs
        self.parent.max_time_temp = int(
                self.parent.edf_info_temp.nsamples[0] / self.parent.edf_info_temp.fs)
        self.channel_info.edf_fn = self.TEST_FN
        self.parent.fn_full_temp = self.TEST_FN
        self.parent.fn_temp = self.TEST_FN.split("/")[-1]

        self.ui = ChannelOptions(self.channel_info, self.parent)

    # 0. channel_options.py
    def test_populate_chns(self):
        # Check that channels are populated correctly
        chn_items = []
        for it in self.ui.chn_items:
            chn_items.append(it.text())
        self.assertEqual(chn_items, list(self.channel_info.labels2chns.keys()))
    
    def test_click_ar_cbox(self):
        # Check that clicking AR checks the correct channels
        self.assertEqual(self.ui.cbox_ar.isChecked(),0)
        self.assertEqual(self.ui.cbox_bip.isChecked(),0)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        self.assertEqual(selected_list_items, [])
        QTest.mouseClick(self.ui.cbox_ar, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_ar.isChecked(),1)
        self.assertEqual(self.ui.cbox_bip.isChecked(),0)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        selected_list_names = []
        for it in selected_list_items:
            selected_list_names.append(it.text())
        selected_list_names.sort()
        self.LABELS_AR1020.sort()
        self.assertEqual(selected_list_names, self.LABELS_AR1020)
    
    def test_click_bip_cbox(self):
        # Check that clicking BIP checks the correct channels
        self.assertEqual(self.ui.cbox_ar.isChecked(),0)
        self.assertEqual(self.ui.cbox_bip.isChecked(),0)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        self.assertEqual(selected_list_items, [])
        QTest.mouseClick(self.ui.cbox_bip, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_ar.isChecked(),0)
        self.assertEqual(self.ui.cbox_bip.isChecked(),1)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        selected_list_names = []
        for it in selected_list_items:
            selected_list_names.append(it.text())
        selected_list_names.sort()
        self.LABELS_AR1020.sort()
        self.assertEqual(selected_list_names, self.LABELS_AR1020)

    def test_check_chns_valid(self):
        # Check that check chns works if you give it valid channel names
        ret = self.ui._check_chns(self.TEST_TXT_FILE, "uw_chns.txt")
        self.assertEqual(ret, 1)
        txt_file_chns = ["C4", "T2", "PZ", "FP1"]
        self.assertEqual(txt_file_chns,
            self.channel_info.labels_from_txt_file["uw_chns.txt"])

    def test_check_chns_invalid(self):
        # Check that check chns will reject a file with invalid names
        ret = self.ui._check_chns(self.TEST_INVALID_TXT_FILE, "uw_chns.txt")
        self.assertEqual(ret, 0)
        self.assertEqual(self.channel_info.labels_from_txt_file, {})
        
    def test_add_text_file(self):
        # Test once you have the text file added
        self.ui._check_chns(self.TEST_TXT_FILE, "uw_chns.txt")
        self.ui.add_txt_file("uw_chns.txt")
        for child in self.ui.chn_cbox_list.children():
            for ch in child.children():
                if isinstance(ch, QCheckBox):
                    if ch.text() != "uw_chns.txt":
                        self.assertEqual(ch.isChecked(), 0)
                    else:
                        self.assertEqual(ch.isChecked(), 1)
        self.assertEqual(self.ui.cbox_ar.isChecked(), 0)
        self.assertEqual(self.ui.cbox_bip.isChecked(), 0)
        self.assertEqual(self.channel_info.use_loaded_txt_file, 1)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        txt_file_chns = ["C4", "T2", "PZ", "FP1"]
        selected_list_names = []
        for it in selected_list_items:
            selected_list_names.append(it.text())
        selected_list_names.sort()
        txt_file_chns.sort()
        self.assertEqual(selected_list_names, txt_file_chns)

    def test_uncheck_txt_files(self):
        # Check that unchecking all test files works
        self.ui._check_chns(self.TEST_TXT_FILE, "uw_chns.txt")
        self.ui.add_txt_file("uw_chns.txt")
        self.ui.uncheck_txt_files()
        for child in self.ui.chn_cbox_list.children():
            for grand_child in child.children():
                if isinstance(grand_child, QCheckBox):
                    self.assertEqual(grand_child.isChecked(), 0)
    
    def test_get_mont_type(self):
        # Test getting the montage type
        self.ui.cbox_ar.setChecked(1)
        ret, txt_fn = self.ui._get_mont_type()
        self.assertEqual(ret, 0)
        self.assertEqual(txt_fn, "")

        self.ui.cbox_bip.setChecked(1)
        ret, txt_fn = self.ui._get_mont_type()
        self.assertEqual(ret, 1)
        self.assertEqual(txt_fn, "")

        self.ui._check_chns(self.TEST_TXT_FILE, "uw_chns.txt")
        self.ui.add_txt_file("uw_chns.txt")
        ret, txt_fn = self.ui._get_mont_type()
        self.assertEqual(ret, 4)
        self.assertEqual(txt_fn, "uw_chns.txt")

    def test_check(self):
        # Test that the check function works properly
        QTest.mouseClick(self.ui.cbox_bip, Qt.LeftButton)
        ret = self.ui.check()
        self.assertEqual(ret, 0)
    
    # 1. channel_info.py
    def test_convert_txt_chn_names(self):
        # Test channel conversion
        ret = convert_txt_chn_names("t1")
        self.assertEqual(ret, "T1")
        ret = convert_txt_chn_names("EEG t1")
        self.assertEqual(ret, "T1")
        ret = convert_txt_chn_names("t1-REF")
        self.assertEqual(ret, "T1")
        ret = convert_txt_chn_names("EEG t7")
        self.assertEqual(ret, "T3")
        ret = convert_txt_chn_names("P7")
        self.assertEqual(ret, "T5")
        ret = convert_txt_chn_names("T8")
        self.assertEqual(ret, "T4")
        ret = convert_txt_chn_names("P8")
        self.assertEqual(ret, "T6")
        ret = convert_txt_chn_names("T7-T1")
        self.assertEqual(ret, "T3-T1")
        ret = convert_txt_chn_names("T7-T7")
        self.assertEqual(ret, "T3-T3")
        ret = convert_txt_chn_names("P7-T7")
        self.assertEqual(ret, "T5-T3")
        ret = convert_txt_chn_names("T8-T7")
        self.assertEqual(ret, "T4-T3")
        ret = convert_txt_chn_names("P8-T7")
        self.assertEqual(ret, "T6-T3")
        ret = convert_txt_chn_names("T1-P7")
        self.assertEqual(ret, "T1-T5")
        ret = convert_txt_chn_names("T1-T8")
        self.assertEqual(ret, "T1-T4")
        ret = convert_txt_chn_names("T1-P8")
        self.assertEqual(ret, "T1-T6")

    def test_check_label(self):
        # Test check label
        test_chn_list = {"t1-REF": 0, "EEG T2": 1, "T3": 2}
        ret = _check_label("T1", test_chn_list)
        self.assertEqual(ret, 0)

        ret = _check_label("T2", test_chn_list)
        self.assertEqual(ret, 1)

        ret = _check_label("T3", test_chn_list)
        self.assertEqual(ret, 2)

        ret = _check_label("T7", test_chn_list)
        self.assertEqual(ret, 2)

        ret = _check_label("T8", test_chn_list)
        self.assertEqual(ret, -1)
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)