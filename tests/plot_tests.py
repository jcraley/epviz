""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
import numpy as np
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
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/E_B_1-DeID_0003.edf"
        patch('sys.argv', ["--show","0"])
        args = get_args()
        check_args(args)
        self.plot_window = MainPage(args, app)

    # 0. Initialization
    def test_init_values(self):
        # Check that values are initialized properly
        self.assertEqual(self.plot_window.count, 0)
        self.assertEqual(self.plot_window.init, 0)
        self.assertEqual(self.plot_window.window_size, 10)
        self.assertEqual(self.plot_window.filter_checked, 0)
        self.assertEqual(self.plot_window.ylim, [150,100])
        self.assertEqual(self.plot_window.max_channels, 70)
        self.assertEqual(self.plot_window.filter_win_open, 0)
        self.assertEqual(self.plot_window.preds_win_open, 0)
        self.assertEqual(self.plot_window.chn_win_open, 0)
        self.assertEqual(self.plot_window.organize_win_open, 0)
        self.assertEqual(self.plot_window.color_win_open, 0)
        self.assertEqual(self.plot_window.spec_win_open, 0)
        self.assertEqual(self.plot_window.saveimg_win_open, 0)
        self.assertEqual(self.plot_window.saveedf_win_open, 0)
        self.assertEqual(self.plot_window.anon_win_open, 0)
        self.assertEqual(self.plot_window.savetopo_win_open, 0)
        self.assertEqual(self.plot_window.stat_fs_band_win_open, 0)
        self.assertEqual(self.plot_window.max_time, 0)
        self.assertEqual(self.plot_window.topoplot_line_val, 100)
        self.assertEqual(self.plot_window.topoplot_line, None)
        self.assertEqual(self.plot_window.zoom_roi_pos, (0,0))
        self.assertEqual(self.plot_window.zoom_roi_size, (100,100))
        self.assertEqual(self.plot_window.zoom_roi, None)
        self.assertEqual(self.plot_window.spec_roi_val, [0,100])
        self.assertEqual(self.plot_window.spec_select_time_rect, None)

    # 1. Loading data
    def test_load_data(self):
        # Test that everything is set properly when data is loaded
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)

        self.assertEqual(self.plot_window.edf_file_name_temp, self.TEST_FN)
        self.assertEqual(self.plot_window.fn_full_temp, self.TEST_FN)
        self.assertEqual(self.plot_window.fn_temp, self.TEST_FN.split("/")[-1])
        self.assertEqual(self.plot_window.edf_info_temp.fs, 256)
        self.assertEqual(self.plot_window.max_time_temp, 688)
        self.assertEqual(self.plot_window.chn_win_open, 1)
        self.assertEqual(self.plot_window.predicted, 0)

    def test_init_graph(self):
        # Test that everything is set properly when graph is initialized
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.argv.filter[0] = 1
        self.plot_window.load_data(name=self.TEST_FN)

        self.plot_window.edf_info = self.plot_window.edf_info_temp
        self.plot_window.init_graph()

        self.assertEqual(self.plot_window.init, 0)
        
        self.assertEqual(self.plot_window.fi.lp, self.plot_window.argv.filter[1])
        self.assertEqual(self.plot_window.fi.hp, self.plot_window.argv.filter[2])
        self.assertEqual(self.plot_window.fi.notch, self.plot_window.argv.filter[3])
        self.assertEqual(self.plot_window.fi.bp1, self.plot_window.argv.filter[4])
        self.assertEqual(self.plot_window.fi.bp2, self.plot_window.argv.filter[5])
        self.assertEqual(self.plot_window.fi.do_lp, 1)
        self.assertEqual(self.plot_window.fi.do_hp, 1)
        self.assertEqual(self.plot_window.fi.do_notch, 0)
        self.assertEqual(self.plot_window.fi.do_bp, 0)
        self.assertEqual(self.plot_window.filter_checked, 1)
        self.assertEqual(self.plot_window.cbox_filter.isChecked(), 0)

        self.assertEqual(self.plot_window.ylim, [150, 100])
        self.assertEqual(self.plot_window.window_size, 10)
        self.assertEqual(self.plot_window.ann_list, [])
        self.assertEqual(self.plot_window.rect_list, [])
        self.assertEqual(self.plot_window.aspan_list, [])
        self.assertEqual(self.plot_window.filtered_data, [])
        self.assertEqual(self.plot_window.ws_combobox.currentText().split("s")[0], "10")
        self.assertEqual(self.plot_window.pred_label.text(), "")
        self.assertEqual(self.plot_window.thresh, 0.5)
        self.assertEqual(self.plot_window.thresh_lbl.text(),
                "Change threshold of prediction:  (threshold = 0.5)")

    def test_init_graph_filtered0(self):
        # Test that filter info properties are set correctly if filtered info is
        #   in the annotations
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)

        self.plot_window.edf_info = self.plot_window.edf_info_temp
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            0, [0.0, -1.0, "filtered"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            1, [0.0, -1.0, "LP: 29Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            2, [0.0, -1.0, "HP: 3Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            3, [0.0, -1.0, "N: 5Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            4, [0.0, -1.0, "BP: 0-0Hz"], axis=1)
        self.plot_window.init_graph()
        
        self.assertEqual(self.plot_window.fi.lp, 29)
        self.assertEqual(self.plot_window.fi.hp, 3)
        self.assertEqual(self.plot_window.fi.notch, 5)
        self.assertEqual(self.plot_window.fi.bp1, 0)
        self.assertEqual(self.plot_window.fi.bp2, 0)
        self.assertEqual(self.plot_window.fi.do_lp, 1)
        self.assertEqual(self.plot_window.fi.do_hp, 1)
        self.assertEqual(self.plot_window.fi.do_notch, 1)
        self.assertEqual(self.plot_window.fi.do_bp, 0)
        self.assertEqual(self.plot_window.filter_checked, 1)
        self.assertEqual(self.plot_window.cbox_filter.isChecked(), 0)

    def test_init_graph_filtered1(self):
        # Test that filter info properties are set correctly if filtered info is
        #   in the annotations
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)

        self.plot_window.edf_info = self.plot_window.edf_info_temp
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            0, [0.0, -1.0, "filtered"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            1, [0.0, -1.0, "LP: 0Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            2, [0.0, -1.0, "HP: 0Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            3, [0.0, -1.0, "N: 0Hz"], axis=1)
        self.plot_window.edf_info.annotations = np.insert(self.plot_window.edf_info.annotations,
                                                            4, [0.0, -1.0, "BP: 3-5Hz"], axis=1)
        self.plot_window.init_graph()
        
        self.assertEqual(self.plot_window.fi.lp, 30)
        self.assertEqual(self.plot_window.fi.hp, 2)
        self.assertEqual(self.plot_window.fi.notch, 60)
        self.assertEqual(self.plot_window.fi.bp1, 3)
        self.assertEqual(self.plot_window.fi.bp2, 5)
        self.assertEqual(self.plot_window.fi.do_lp, 0)
        self.assertEqual(self.plot_window.fi.do_hp, 0)
        self.assertEqual(self.plot_window.fi.do_notch, 0)
        self.assertEqual(self.plot_window.fi.do_bp, 1)
        self.assertEqual(self.plot_window.filter_checked, 1)
        self.assertEqual(self.plot_window.cbox_filter.isChecked(), 0)

    def test_call_initial_move_plot(self):
        # Test the functionality of call_initial_move_plot
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.argv.prediction_thresh = 0.7
        self.plot_window.call_initial_move_plot()

        self.assertEqual(self.plot_window.slider.maximum(),
                            self.plot_window.max_time
                            - self.plot_window.window_size)
        self.assertEqual(self.plot_window.thresh_slider.value(), 70)
        self.assertEqual(self.plot_window.init, 1)

    def test_slider(self):
        # Test whether the slider changes count properly
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.argv.prediction_thresh = 0.7
        self.plot_window.call_initial_move_plot()

        self.plot_window.slider.setValue(4)
        self.plot_window.slider_change()
        self.assertEqual(self.plot_window.count, 4)
        self.plot_window.slider.setValue(28)
        self.plot_window.slider_change()
        self.assertEqual(self.plot_window.count, 28)
        self.plot_window.slider.setValue(685)
        self.plot_window.slider_change()
        self.assertEqual(self.plot_window.count, 678)

        self.plot_window.ws_combobox.setCurrentIndex(1)
        self.plot_window.slider.setValue(683)
        self.plot_window.slider_change()
        self.assertEqual(self.plot_window.count, 683)
        self.plot_window.slider.setValue(685)
        self.plot_window.slider_change()
        self.assertEqual(self.plot_window.count, 683)
    
    def test_thresh_slider(self):
        # Test the threshold slider
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.argv.prediction_thresh = 0.7
        self.plot_window.call_initial_move_plot()

        self.plot_window.thresh_slider.setValue(4)
        self.plot_window.change_thresh_slider()
        self.assertEqual(self.plot_window.thresh, 0.04)
        self.assertEqual(self.plot_window.thresh_lbl.text(),
                    "Change threshold of prediction:  (threshold = 0.04)")

    def test_move_plot(self):
        # Test moving the plot left and right
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.call_initial_move_plot()

        self.assertEqual(self.plot_window.count, 0)
        self.plot_window.left_plot_1s()
        self.assertEqual(self.plot_window.count, 0)
        self.plot_window.right_plot_1s()
        self.assertEqual(self.plot_window.count, 1)
        self.plot_window.right_plot_10s()
        self.assertEqual(self.plot_window.count, 11)
        self.plot_window.left_plot_10s()
        self.assertEqual(self.plot_window.count, 1)

    def test_change_amp(self):
        # Test changing the ylim
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.call_initial_move_plot()

        self.assertEqual(self.plot_window.ylim, [150, 100])
        self.plot_window.inc_amp()
        self.assertEqual(self.plot_window.ylim, [135, 90])
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.plot_window.inc_amp()
        self.assertEqual(self.plot_window.ylim, [45, 30])
        self.plot_window.dec_amp()
        self.assertEqual(self.plot_window.ylim, [60, 40])

    def test_update_normal_time(self):
        # Test the time ann label updates properly
        self._load_signals()

        # Before changing
        self.assertEqual(self.plot_window.ann_time_edit_time.time().second(), 0)
        self.assertEqual(self.plot_window.ann_time_edit_time.time().minute(), 0)
        self.assertEqual(self.plot_window.ann_time_edit_time.time().hour(), 0)
        self.assertEqual(self.plot_window.ann_time_edit_count.value(), 0)
        self.assertEqual(self.plot_window.ann_duration.minimum(), 0)
        self.assertEqual(self.plot_window.ann_duration.maximum(), 99)

        self.plot_window.ann_time_edit_count.setValue(27)
        self.plot_window.update_normal_time()
        # After changing
        self.assertEqual(self.plot_window.ann_time_edit_time.time().second(), 27)
        self.assertEqual(self.plot_window.ann_time_edit_time.time().minute(), 0)
        self.assertEqual(self.plot_window.ann_time_edit_time.time().hour(), 0)
        self.assertEqual(self.plot_window.ann_time_edit_count.value(), 27)
        self.assertEqual(self.plot_window.ann_duration.minimum(), -1)
        self.assertEqual(self.plot_window.ann_duration.maximum(), 688 - 27)

    def _load_signals(self):
        # for loading in the test file
        self.plot_window.argv.show = 0
        self.plot_window.argv.fn = self.TEST_FN
        self.plot_window.load_data(name=self.TEST_FN)
        self.plot_window.chn_ops.cbox_bip.setChecked(1)
        self.plot_window.chn_ops.check()
        self.plot_window.call_initial_move_plot()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
