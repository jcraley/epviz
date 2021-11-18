""" Module for testing the filter options window """
import sys
import os
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QDate, QTime
from image_saving.saveImg_options import SaveImgOptions
from image_saving.saveImg_info import SaveImgInfo
from image_saving.saveTopoplot_options import SaveTopoplotOptions, _get_dim
from predictions.prediction_options import PredictionOptions
from plot import MainPage, check_args, get_args

import numpy as np

import datetime

app = QApplication([])
class TestImgSaving(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "test_files/chb.edf"
        self.TEST_FN_ANN = "test_files/tuh_with_annotations.edf"
        self.TEST_PREDS_MULTICHN = "test_files/chb_multichannel.pt"
        sys.argv = ['visualization/plot.py']
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        self._load_signals()
        self.saveimg_info = SaveImgInfo()
        # Set info
        self.saveimg_info.ylim = self.parent.ylim[0]
        fs = self.parent.edf_info.fs
        plot_data = np.zeros((self.parent.ci.nchns_to_plot, self.parent.window_size * fs))
        plot_data += self.parent.ci.data_to_plot[:,
                    self.parent.count * fs:(self.parent.count + self.parent.window_size) * fs]
        stddev = np.std(plot_data)
        plot_data[plot_data > 5 * stddev] = 5 * stddev  # float('nan') # clip amplitude
        plot_data[plot_data < -5 * stddev] = -5 * stddev
        self.saveimg_info.data = plot_data
        self.saveimg_info.pi = self.parent.pi
        self.saveimg_info.ci = self.parent.ci
        self.saveimg_info.predicted = self.parent.predicted
        self.saveimg_info.fs = self.parent.edf_info.fs
        self.saveimg_info.count = self.parent.count
        self.saveimg_info.window_size = self.parent.window_size
        self.saveimg_info.thresh = self.parent.thresh

        self.ui = SaveImgOptions(self.saveimg_info, self.parent)
        self.ui_topo = SaveTopoplotOptions(self.parent)

    def test_setup_saveimg_options(self):
        # Test that everything is checked properly at startup
        self.assertEqual(self.saveimg_info.plot_ann, 1)
        self.assertEqual(self.saveimg_info.line_thick, 0.5)
        self.assertEqual(self.saveimg_info.font_size, 12)
        self.assertEqual(self.saveimg_info.plot_title, 0)
        self.assertEqual(self.saveimg_info.title, "")

        self.saveimg_info.line_thick = 1
        self.saveimg_info.title = "test"

        # Test that reset initial state works
        self.ui.reset_initial_state()

        self.assertEqual(self.saveimg_info.plot_ann, 1)
        self.assertEqual(self.saveimg_info.line_thick, 0.5)
        self.assertEqual(self.saveimg_info.font_size, 12)
        self.assertEqual(self.saveimg_info.plot_title, 0)
        self.assertEqual(self.saveimg_info.title, "")

    def test_check_ann(self):
        # Test showing annotations
        self.assertEqual(self.saveimg_info.plot_ann, 1)
        self.assertTrue(self.ui.sio_ui.annCbox.isChecked())
        self.ui.sio_ui.annCbox.setChecked(0)
        self.ui.ann_checked()
        self.assertEqual(self.saveimg_info.plot_ann, 0)
        self.assertFalse(self.ui.sio_ui.annCbox.isChecked())

    def test_change_line_thick(self):
        # Test changing line thickness
        self.assertEqual(self.ui.sio_ui.lineThickInput.currentIndex(), 1)
        self.assertEqual(self.saveimg_info.line_thick, 0.5)
        self.assertEqual(self.ui.sio_ui.lineThickInput.currentText(), "0.5px")
        self.ui.sio_ui.lineThickInput.setCurrentIndex(4)
        self.assertEqual(self.ui.sio_ui.lineThickInput.currentIndex(), 4)
        self.assertEqual(self.ui.sio_ui.lineThickInput.currentText(), "1.25px")
        self.assertEqual(self.saveimg_info.line_thick, 1.25)

    def test_change_text_size(self):
        # Test changing font size
        self.assertEqual(self.ui.sio_ui.textSizeInput.currentIndex(), 3)
        self.assertEqual(self.saveimg_info.font_size, 12)
        self.assertEqual(self.ui.sio_ui.textSizeInput.currentText(), "12pt")
        self.ui.sio_ui.textSizeInput.setCurrentIndex(0)
        self.assertEqual(self.ui.sio_ui.textSizeInput.currentIndex(), 0)
        self.assertEqual(self.ui.sio_ui.textSizeInput.currentText(), "6pt")
        self.assertEqual(self.saveimg_info.font_size, 6)

    def test_add_title(self):
        # Test adding a tile to the plot
        self.assertEqual(self.ui.sio_ui.titleCbox.isChecked(), 0)
        self.assertEqual(self.saveimg_info.title, "")
        self.assertEqual(self.ui.sio_ui.titleInput.text(), "")

        self.ui.sio_ui.titleInput.setText("Title0")
        self.assertEqual(self.ui.sio_ui.titleCbox.isChecked(), 0)
        self.assertEqual(self.saveimg_info.title, "")
        self.assertEqual(self.ui.sio_ui.titleInput.text(), "Title0")

        self.ui.sio_ui.titleCbox.setChecked(1)
        self.ui.title_checked()
        self.assertEqual(self.ui.sio_ui.titleCbox.isChecked(), 1)
        self.assertEqual(self.saveimg_info.title, "Title0")
        self.assertEqual(self.ui.sio_ui.titleInput.text(), "Title0")
        self.assertEqual(self.ui.ax.get_title(), "Title0")

        self.ui.sio_ui.titleInput.setText("Title1")
        self.ui.title_changed()
        self.assertEqual(self.ui.sio_ui.titleCbox.isChecked(), 1)
        self.assertEqual(self.saveimg_info.title, "Title1")
        self.assertEqual(self.ui.sio_ui.titleInput.text(), "Title1")
        self.assertEqual(self.ui.ax.get_title(), "Title1")

        self.ui.sio_ui.titleCbox.setChecked(0)
        self.ui.title_checked()
        self.assertEqual(self.ui.sio_ui.titleCbox.isChecked(), 0)
        self.assertEqual(self.saveimg_info.title, "")
        self.assertEqual(self.ui.sio_ui.titleInput.text(), "Title1")
        self.assertEqual(self.ui.ax.get_title(), "")

    def test_print_plot(self):
        # Basically just make a plot and make sure that the
        # file is actually created
        self.parent.argv.export_png_file = "unittest_png_file"
        self.parent.init = 0
        self.parent.argv.show = 1
        self.ui.print_plot()
        
        self.assertTrue(os.path.exists("unittest_png_file.png"))
        if os.path.exists("unittest_png_file.png"):
            os.remove("unittest_png_file.png")

    def test_annotations_work(self):
        # Test a file with annotations and test command line options
        self._load_signals2()
        self.saveimg_info = SaveImgInfo()
        # Set info
        self.saveimg_info.ylim = self.parent.ylim[0]
        fs = self.parent.edf_info.fs
        plot_data = np.zeros((self.parent.ci.nchns_to_plot, self.parent.window_size * fs))
        plot_data += self.parent.ci.data_to_plot[:,
                    self.parent.count * fs:(self.parent.count + self.parent.window_size) * fs]
        stddev = np.std(plot_data)
        plot_data[plot_data > 5 * stddev] = 5 * stddev  # float('nan') # clip amplitude
        plot_data[plot_data < -5 * stddev] = -5 * stddev
        self.saveimg_info.data = plot_data
        self.saveimg_info.pi = self.parent.pi
        self.saveimg_info.ci = self.parent.ci
        self.saveimg_info.predicted = self.parent.predicted
        self.saveimg_info.fs = self.parent.edf_info.fs
        self.saveimg_info.count = self.parent.count
        self.saveimg_info.window_size = self.parent.window_size
        self.saveimg_info.thresh = self.parent.thresh

        self.parent.argv.export_png_file = "unittest_png_file2"
        self.parent.init = 0
        self.parent.argv.show = 1
        self.parent.argv.print_annotations = 1
        self.parent.argv.line_thickness = 0.25
        self.parent.argv.font_size = 8
        self.parent.argv.plot_title = "Test 2"
        self.ui2 = SaveImgOptions(self.saveimg_info, self.parent)

        self.assertTrue(os.path.exists("unittest_png_file2.png"))
        if os.path.exists("unittest_png_file2.png"):
            os.remove("unittest_png_file2.png")

    def test_get_dim(self):
        # Test that getting dimensions works properly
        r, c = _get_dim(45)
        self.assertEqual(r, 6)
        self.assertEqual(c, 8)
        r, c = _get_dim(10)
        self.assertEqual(r, 3)
        self.assertEqual(c, 4)
        r, c = _get_dim(1)
        self.assertEqual(r, 1)
        self.assertEqual(c, 1)

    def test_get_time(self):
        # Test the get time function
        ret = self.ui_topo._get_time(0, 0)
        self.assertEqual(ret, 0)

        ret = self.ui_topo._get_time(3500, 5)
        samples = (3500 + 5) * self.parent.pi.pred_width
        samples = samples / self.parent.edf_info.fs
        self.assertEqual(ret, samples)

        ret = self.ui_topo._get_time(871, 27)
        samples = (871 + 27) * self.parent.pi.pred_width
        samples = samples / self.parent.edf_info.fs
        self.assertEqual(ret, samples)

    def test_get_num_subplots(self):
        count = self.parent.count
        ws = self.parent.window_size
        width = int(self.parent.pi.pred_width)

        num, start = self.ui_topo._get_num_subplots()
        self.assertEqual(num, 5)
        self.assertEqual(start, self.parent.count)

        self.parent.count = 27
        num, start = self.ui_topo._get_num_subplots()
        self.assertEqual(num, 5)
        self.assertEqual(start, (self.parent.count + 1) / 2)

        self.parent.window_size = 30
        num, start = self.ui_topo._get_num_subplots()
        self.assertEqual(num, 15)
        self.assertEqual(start, (self.parent.count + 1) / 2)

        self.ui_topo.plot_single_time = 1
        self.ui_topo.plot_at_time = 98
        num, start = self.ui_topo._get_num_subplots()
        self.assertEqual(num, 1)
        self.assertEqual(start, 98)

    def test_get_pred_sample_from_time(self):
        # Test the function to get the sample from time
        ret = self.ui_topo._get_pred_sample_from_time(0.1)
        self.assertEqual(ret, 0)

        ret = self.ui_topo._get_pred_sample_from_time(3527.2)
        val_samples = 3527.2 * self.parent.edf_info.fs
        pred_loc = int(val_samples / self.parent.pi.pred_width)
        self.assertEqual(ret, pred_loc)

    def test_plot_single_time(self):
        # Test plotting a single time
        self.assertFalse(self.ui_topo.cbox_single_time.isChecked())
        self.assertEqual(self.ui_topo.plot_single_time, 0)

        self.ui_topo.cbox_single_time.setChecked(1)
        self.ui_topo.toggle_plot_single_time()

        self.assertTrue(self.ui_topo.cbox_single_time.isChecked())
        self.assertEqual(self.ui_topo.plot_single_time, 1)
        self.assertEqual(self.ui_topo.plot_at_time, 0)

        self.ui_topo.cbox_single_time.setChecked(0)
        self.ui_topo.spinbox_single_time.setValue(27.2)
        self.ui_topo.change_single_time()

        self.assertFalse(self.ui_topo.cbox_single_time.isChecked())
        self.assertEqual(self.ui_topo.plot_single_time, 0)
        self.assertEqual(self.ui_topo.plot_at_time, 13)

    def test_topo_change_title(self):
        # Test changing the title for topoplots
        self.assertEqual(self.ui_topo.cbox_title.isChecked(), 0)
        self.assertEqual(self.ui_topo.plot_title, "")
        self.assertEqual(self.ui_topo.title_input.text(), "")

        self.ui_topo.title_input.setText("Title0")
        self.assertEqual(self.ui_topo.cbox_title.isChecked(), 0)
        self.assertEqual(self.ui_topo.plot_title, "")
        self.assertEqual(self.ui_topo.title_input.text(), "Title0")

        self.ui_topo.cbox_title.setChecked(1)
        self.ui_topo.title_checked()
        self.assertEqual(self.ui_topo.cbox_title.isChecked(), 1)
        self.assertEqual(self.ui_topo.plot_title, "Title0")
        self.assertEqual(self.ui_topo.title_input.text(), "Title0")
        self.assertEqual(self.ui_topo.m.fig._suptitle.get_text(), "Title0")

        self.ui_topo.title_input.setText("Title1")
        self.ui_topo.title_changed()
        self.assertEqual(self.ui_topo.cbox_title.isChecked(), 1)
        self.assertEqual(self.ui_topo.plot_title, "Title1")
        self.assertEqual(self.ui_topo.title_input.text(), "Title1")
        self.assertEqual(self.ui_topo.m.fig._suptitle.get_text(), "Title1")

        self.ui_topo.cbox_title.setChecked(0)
        self.ui_topo.title_checked()
        self.assertEqual(self.ui_topo.cbox_title.isChecked(), 0)
        self.assertEqual(self.ui_topo.plot_title, "")
        self.assertEqual(self.ui_topo.title_input.text(), "Title1")
        self.assertEqual(self.ui_topo.m.fig._suptitle.get_text(), "")

    def test_add_times(self):
        # Test adding times to topoplots
        self.assertEqual(self.ui_topo.cbox_add_times.isChecked(), 0)
        self.assertEqual(self.ui_topo.show_subplot_times, 0)

        self.ui_topo.cbox_add_times.setChecked(1)
        self.ui_topo.add_times()
        title = ["0.0s", "2.0s", "4.0s", "6.0s", "8.0s"]
        for i in range(len(self.ui_topo.ax)):
            self.assertEqual(self.ui_topo.ax[i].get_title(), title[i])
        self.assertEqual(self.ui_topo.cbox_add_times.isChecked(), 1)
        self.assertEqual(self.ui_topo.show_subplot_times, 1)

    def _load_signals(self):
        # for loading in the test file and predictions
        self.parent.argv.show = 0
        self.parent.argv.fn = self.TEST_FN
        self.parent.load_data(name=self.TEST_FN)
        self.parent.chn_ops.cbox_bip.setChecked(1)
        self.parent.chn_ops.check()
        self.parent.call_initial_move_plot()

        self.pred_ops = PredictionOptions(self.parent.pi, self.parent)
        self.parent.pi.set_preds(self.TEST_PREDS_MULTICHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.pred_ops.cbox_preds.setChecked(1)
        self.pred_ops.check()

    def _load_signals2(self):
        # Make sure a file with annotations works as well
        self.parent.init = 0
        self.parent.argv.show = 0
        self.parent.predicted = 0
        self.parent.argv.fn = self.TEST_FN_ANN
        self.parent.load_data(name=self.TEST_FN_ANN)
        self.parent.chn_ops.cbox_bip.setChecked(1)
        self.parent.chn_ops.check()
        self.parent.call_initial_move_plot()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)