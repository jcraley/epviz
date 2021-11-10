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
        self.LABELS_AR1020_TEST_FILE = ["EEG O2-REF","EEG O1-REF","EEG PZ-REF",
                            "EEG CZ-REF","EEG FZ-REF","EEG T6-REF","EEG T5-REF",
                            "EEG T4-REF","EEG T3-REF","EEG F8-REF","EEG F7-REF",
                            "EEG P4-REF","EEG P3-REF","EEG C4-REF","EEG C3-REF",
                            "EEG F4-REF","EEG F3-REF","EEG FP2-REF","EEG FP1-REF"]
        # Set the test files
        self.TEST_FN = "test_files/tuh.edf"
        self.TEST_TXT_FILE = "test_files/tuh_chns_valid.txt"
        self.TEST_INVALID_TXT_FILE = "test_files/tuh_chns_invalid.txt"
        self.TEST_FN_PREDS = "test_files/chb_with_saved_preds.edf"
        # Load in the file
        loader = EdfLoader()
        self.parent.edf_info_temp = loader.load_metadata(self.TEST_FN)
        # Create the ChannelInfo object
        self.channel_info = ChannelInfo()
        self.channel_info.chns2labels = self.parent.edf_info_temp.chns2labels
        self.channel_info.labels2chns = self.parent.edf_info_temp.labels2chns
        self.channel_info.fs = self.parent.edf_info_temp.fs
        self.parent.max_time_temp = int(
                self.parent.edf_info_temp.nsamples[0] / self.parent.edf_info_temp.fs[0])
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
        self.LABELS_AR1020_TEST_FILE.sort()
        self.assertEqual(selected_list_names, self.LABELS_AR1020_TEST_FILE)
    
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
        self.LABELS_AR1020_TEST_FILE.sort()
        self.assertEqual(selected_list_names, self.LABELS_AR1020_TEST_FILE)

    def test_check_chns_valid(self):
        # Check that check chns works if you give it valid channel names
        ret = self.ui._check_chns(self.TEST_TXT_FILE, "test_chns.txt")
        self.assertEqual(ret, 1)
        txt_file_chns = ["C4", "T2", "PZ", "FP1"]
        self.assertEqual(txt_file_chns,
            self.channel_info.labels_from_txt_file["test_chns.txt"])

    def test_check_chns_invalid(self):
        # Check that check chns will reject a file with invalid names
        ret = self.ui._check_chns(self.TEST_INVALID_TXT_FILE, "test_chns.txt")
        self.assertEqual(ret, 0)
        self.assertEqual(self.channel_info.labels_from_txt_file, {})
        
    def test_add_text_file(self):
        # Test once you have the text file added
        self.ui._check_chns(self.TEST_TXT_FILE, "test_chns.txt")
        self.ui.add_txt_file("test_chns.txt")
        for child in self.ui.chn_cbox_list.children():
            for ch in child.children():
                if isinstance(ch, QCheckBox):
                    if ch.text() != "test_chns.txt":
                        self.assertEqual(ch.isChecked(), 0)
                    else:
                        self.assertEqual(ch.isChecked(), 1)
        self.assertEqual(self.ui.cbox_ar.isChecked(), 0)
        self.assertEqual(self.ui.cbox_bip.isChecked(), 0)
        self.assertEqual(self.channel_info.use_loaded_txt_file, 1)
        selected_list_items = self.ui.chn_qlist.selectedItems()
        txt_file_chns = ["EEG C4-REF", "EEG T2-REF", "EEG PZ-REF", "EEG FP1-REF"]
        selected_list_names = []
        for it in selected_list_items:
            selected_list_names.append(it.text())
        selected_list_names.sort()
        txt_file_chns.sort()
        self.assertEqual(selected_list_names, txt_file_chns)

    def test_load_text_file(self):
        # Test loading a text file
        self.parent.argv.montage_file = self.TEST_TXT_FILE
        self.ui.load_txt_file(self.TEST_TXT_FILE)

    def test_uncheck_txt_files(self):
        # Check that unchecking all test files works
        self.ui._check_chns(self.TEST_TXT_FILE, "test_chns.txt")
        self.ui.add_txt_file("test_chns.txt")
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

        self.ui._check_chns(self.TEST_TXT_FILE, "test_chns.txt")
        self.ui.add_txt_file("test_chns.txt")
        ret, txt_fn = self.ui._get_mont_type()
        self.assertEqual(ret, 4)
        self.assertEqual(txt_fn, "test_chns.txt")

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

    def test_get_color(self):
        # Test the _get_color method
        ret = self.channel_info._get_color("FP1")
        self.assertEqual(ret, self.channel_info.lt_col)
        self.channel_info.lt_col = "k"
        ret = self.channel_info._get_color("FP1")
        self.assertEqual(ret, self.channel_info.lt_col)
        ret = self.channel_info._get_color("FPZ")
        self.assertEqual(ret, self.channel_info.mid_col)
        ret = self.channel_info._get_color("P2-P4")
        self.assertEqual(ret, self.channel_info.rt_col)
    
    def test_can_do_bip_ar(self):
        # Test can_do_bip_ar
        labelsBIP1020 = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        labelsAR1020 = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]

        labelsAR1010 = ["IZ","O2","O1","OZ","POZ","PZ","CPZ","CZ","FCZ",
                             "FZ","AFZ","FPZ","P10","P9","TP10","TP9","A2","A1",
                             "T10","T9","FT10","FT9","F10","F9","PO8","PO7",
                             "P8","P7","TP8","TP7","T8","T7","FT8","FT7","F8",
                             "F7","AF8","AF7","FP2","FP1","P6","P5","CP6","CP5",
                             "C6","C5","FC6","FC5","F6","F5","PO4","PO3","P4",
                             "P3","CP4","CP3","C4","C3","FC4","FC3","F4","F3",
                             "AF4","AF3","P2","P1","CP2","CP1","C2","C1","FC2",
                             "FC1","F2","F1","NZ"]
        self.channel_info.converted_chn_names = [k for k in labelsBIP1020]
        # ar1010 = 1, 1
        # ar1020 = 1, 0
        # bip1020 = 0, 0
        ret = self.channel_info.can_do_bip_ar(1, 1)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(1, 0)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(0, 1)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(0, 0)
        self.assertEqual(ret, 1)

        self.channel_info.converted_chn_names = [k for k in labelsAR1010]
        ret = self.channel_info.can_do_bip_ar(1, 1)
        self.assertEqual(ret, 1)
        ret = self.channel_info.can_do_bip_ar(1, 0)
        self.assertEqual(ret, 1)
        ret = self.channel_info.can_do_bip_ar(0, 0)
        self.assertEqual(ret, 0)

        self.channel_info.converted_chn_names = [k for k in labelsAR1020]
        ret = self.channel_info.can_do_bip_ar(1, 1)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(1, 0)
        self.assertEqual(ret, 1)
        ret = self.channel_info.can_do_bip_ar(0, 0)
        self.assertEqual(ret, 0)

        self.channel_info.converted_chn_names = [k for k in labelsAR1020 if k != "O2"]
        ret = self.channel_info.can_do_bip_ar(1, 1)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(1, 0)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(0, 0)
        self.assertEqual(ret, 0)

        self.channel_info.converted_chn_names = [k for k in labelsAR1020]
        self.channel_info.converted_chn_names.append("test")
        ret = self.channel_info.can_do_bip_ar(1, 1)
        self.assertEqual(ret, 0)
        ret = self.channel_info.can_do_bip_ar(1, 0)
        self.assertEqual(ret, 1)
        ret = self.channel_info.can_do_bip_ar(0, 0)
        self.assertEqual(ret, 0)

    def test_prepare_to_plot0(self):
        # Test prepare to plot
        labelsBIP1020 = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        labelsAR1020 = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        self.channel_info.converted_chn_names = [k for k in labelsAR1020]
        self.channel_info.prepare_to_plot(list(range(0,len(labelsAR1020))), self.parent, 0,
                            plot_bip_from_ar = 0, txt_file_name = "")
        self.assertEqual(self.channel_info.nchns_to_plot, len(labelsAR1020))
        self.assertEqual(len(self.channel_info.labels_to_plot), self.channel_info.nchns_to_plot + 1)
        self.assertEqual(self.channel_info.labels_to_plot, ["Notes"] + labelsAR1020)
        for c, l in zip(self.channel_info.colors, self.channel_info.labels_to_plot[1:]):
            self.assertEqual(c, self.channel_info._get_color(l))

    def test_prepare_to_plot1(self):
        # Test prepare to plot
        labelsBIP1020 = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        labelsAR1020 = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        self.channel_info.converted_chn_names = [k for k in labelsAR1020]
        self.channel_info.prepare_to_plot([0, 2, 5, 8, 9], self.parent, 0,
                            plot_bip_from_ar = 0, txt_file_name = "")
        self.assertEqual(self.channel_info.nchns_to_plot, 5)
        self.assertEqual(len(self.channel_info.labels_to_plot), self.channel_info.nchns_to_plot + 1)
        self.assertEqual(self.channel_info.labels_to_plot, ["Notes"] + ["O2", "PZ", "P8", "T7", "F8"])
        for c, l in zip(self.channel_info.colors, self.channel_info.labels_to_plot[1:]):
            self.assertEqual(c, self.channel_info._get_color(l))

    def test_prepare_to_plot2(self):
        # Test prepare to plot
        labelsBIP1020 = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        labelsBIP_organized = ["FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","CZ-PZ","FP1-F7"]
        labelsAR1020 = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        self.channel_info.converted_chn_names = [k for k in labelsAR1020]
        self.channel_info.prepare_to_plot(list(range(0,len(labelsAR1020))), self.parent, 1,
                            plot_bip_from_ar = 1, txt_file_name = "")
        self.assertEqual(self.channel_info.nchns_to_plot, len(labelsBIP1020))
        self.assertEqual(len(self.channel_info.labels_to_plot), self.channel_info.nchns_to_plot + 1)
        self.assertEqual(self.channel_info.labels_to_plot, ["Notes"] + labelsBIP1020)
        for c, l in zip(self.channel_info.colors, self.channel_info.labels_to_plot[1:]):
            self.assertEqual(c, self.channel_info._get_color(l))
        
        self.channel_info.organize = 1
        self.channel_info.labels_to_plot = ["Notes"] + labelsBIP_organized
        self.channel_info.mid_col = "k"
        self.channel_info.prepare_to_plot(list(range(0,len(labelsAR1020))), self.parent, 1,
                            plot_bip_from_ar = 1, txt_file_name = "")
        self.assertEqual(self.channel_info.nchns_to_plot, len(labelsBIP1020))
        self.assertEqual(len(self.channel_info.labels_to_plot), self.channel_info.nchns_to_plot + 1)
        self.assertEqual(self.channel_info.labels_to_plot, ["Notes"] + labelsBIP_organized)
        for c, l in zip(self.channel_info.colors, self.channel_info.labels_to_plot[1:]):
            self.assertEqual(c, self.channel_info._get_color(l))
    
    def test_prepare_to_plot3(self):
        # Test prepare to plot
        labelsBIP1020 = ["CZ-PZ","FZ-CZ","P4-O2","C4-P4","F4-C4","FP2-F4",
                              "P3-O1","C3-P3","F3-C3","FP1-F3","P8-O2","T8-P8",
                              "F8-T8","FP2-F8","P7-O1","T7-P7","F7-T7","FP1-F7"]
        labelsAR1020 = ["O2","O1","PZ","CZ","FZ","P8","P7","T8","T7","F8",
                             "F7","P4","P3","C4","C3","F4","F3","FP2","FP1"]
        self.channel_info.converted_chn_names = [k for k in labelsAR1020] + ["A1"]
        self.channel_info.prepare_to_plot([0, 2, 5, 8, 19], self.parent, 0,
                            plot_bip_from_ar = 0, txt_file_name = "")
        self.assertEqual(self.channel_info.nchns_to_plot, 5)
        self.assertEqual(len(self.channel_info.labels_to_plot), self.channel_info.nchns_to_plot + 1)
        self.assertEqual(self.channel_info.labels_to_plot, ["Notes"] + ["A1", "O2", "PZ", "P8", "T7"])
        for c, l in zip(self.channel_info.colors, self.channel_info.labels_to_plot[1:]):
            self.assertEqual(c, self.channel_info._get_color(l))

    def test_loading_file_with_predictions(self):
        # Test that loading predictions in a file works
        loader = EdfLoader()
        self.parent.edf_info_temp = loader.load_metadata(self.TEST_FN_PREDS)
        # Create the ChannelInfo object
        self.channel_info = ChannelInfo()
        self.channel_info.chns2labels = self.parent.edf_info_temp.chns2labels
        self.channel_info.labels2chns = self.parent.edf_info_temp.labels2chns
        self.channel_info.fs = self.parent.edf_info_temp.fs[0]
        self.parent.max_time_temp = int(
                self.parent.edf_info_temp.nsamples[0] / self.parent.edf_info_temp.fs[0])
        self.channel_info.edf_fn = self.TEST_FN_PREDS
        self.parent.fn_full_temp = self.TEST_FN_PREDS
        self.parent.fn_temp = self.TEST_FN_PREDS.split("/")[-1]

        self.ui2 = ChannelOptions(self.channel_info, self.parent)

        print()
        for x, y in zip(self.ui2.pi.preds_to_plot, self.ui2.data.pred_chn_data):
            self.assertEqual(x, y)
        self.assertEqual(self.ui2.pi.preds_loaded, 1)
        self.assertEqual(self.ui2.pi.plot_loaded_preds, 1)
        self.assertEqual(self.ui2.pi.preds_fn, "loaded from .edf file")
        self.assertEqual(self.ui2.pi.pred_width, (self.ui2.data.fs
                                * self.parent.max_time_temp) / self.ui2.pi.preds.shape[0])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)