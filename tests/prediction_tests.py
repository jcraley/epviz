""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from visualization.predictions.prediction_options import PredictionOptions
from visualization.predictions.prediction_info import PredictionInfo
from visualization.plot import MainPage
from visualization.plot import check_args, get_args
from unittest.mock import patch

import torch
import numpy as np
import datetime

app = QApplication([])
class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/chb01_03.edf"
        self.TEST_MODEL = "/Users/daniellecurrey/Desktop/gui_edf_files/model.pt"
        self.TEST_DATA = "/Users/daniellecurrey/Desktop/gui_edf_files/chb01_03_feats.pt"
        self.TEST_PREDS = "/Users/daniellecurrey/Desktop/gui_edf_files/chb01_03_preds.pt"
        self.TEST_PREDS_MULTICLASS = "/Users/daniellecurrey/Desktop/gui_edf_files/test_chb01_03_multiclass.pt"
        self.TEST_PREDS_MULTICHN = "/Users/daniellecurrey/Desktop/gui_edf_files/test_chb01_03_multichannel.pt"
        self.TEST_PREDS_MULTI_CLASS_CHN = "/Users/daniellecurrey/Desktop/gui_edf_files/test_chb01_03_multiclass_multichannel.pt"
        patch('sys.argv', ["--show","0"])
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        # self.parent.argv.save_edf_fn = "/Users/daniellecurrey/Desktop/test0.edf"
        self._load_signals()
        self.preds_info = PredictionInfo()
        self.ui = PredictionOptions(self.preds_info, self.parent)

    def test_setup(self):
        # Test that everything is checked properly at startup
        self.assertEqual(self.preds_info.predicted, 0)

    def test_return_no_preds(self):
        # Test that if you click out with nothing selected no predictions will be plotted
        self.ui.check()
        self.assertEqual(self.preds_info.predicted, 0)

    def test_check(self):
        # Test the check function in preds ops

        # Try with loaded preds first
        self.parent.pi = self.preds_info
        self.preds_info.set_preds(self.TEST_PREDS, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.ui.cbox_preds.setChecked(1)
        self.ui.check()
        self.assertEqual(self.parent.predicted, 1)
        for x, y in zip(self.preds_info.preds_to_plot, self.preds_info.preds):
            self.assertEqual(x, y)
        self.assertEqual(self.preds_info.multi_class_preds, self.preds_info.multi_class)
        self.assertEqual(self.parent.pred_label.text(), "Predictions plotted.")

        # Try with model and predictions
        # load the model and data
        self.preds_info.set_model(self.TEST_MODEL)
        self.preds_info.set_data(self.TEST_DATA)

        self.ui.cbox_model.setChecked(1)
        self.ui.check()
        self.assertEqual(self.parent.predicted, 1)
        preds = torch.load(self.TEST_MODEL).predict(torch.load(self.TEST_DATA))
        preds = np.array(preds)
        for x, y in zip(self.preds_info.preds_to_plot, preds):
            self.assertEqual(x, y)
        self.assertEqual(self.preds_info.multi_class_preds, self.preds_info.multi_class)
        self.assertEqual(self.parent.pred_label.text(), "Predictions plotted.")

        # Try with multi-class
        self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                    self.parent.max_time,
                                    self.parent.edf_info.fs,
                                    self.parent.ci.nchns_to_plot,
                                    binary=1)
        self.ui.cbox_preds.setChecked(1)
        self.ui.check()
        self.assertEqual(self.parent.predicted, 1)
        for x, y in zip(self.preds_info.preds_to_plot, self.preds_info.preds):
            for xx, yy in zip(x, y):
                self.assertEqual(xx, yy)
        self.assertEqual(self.preds_info.multi_class_preds, self.preds_info.multi_class)
        self.assertEqual(self.parent.pred_label.text(), "Predictions plotted.")

    def test_load_model_and_data(self):
        # Test loading a model and data

        # load the model
        self.assertEqual(self.preds_info.model_loaded, 0)
        self.assertEqual(self.preds_info.data_loaded, 0)
        self.assertEqual(self.preds_info.ready, 0)
        self.preds_info.set_model(self.TEST_MODEL)
        self.assertEqual(self.preds_info.model_loaded, 1)
        self.assertEqual(self.preds_info.data_loaded, 0)
        self.assertEqual(self.preds_info.ready, 0)

        # load the data
        self.preds_info.set_data(self.TEST_DATA)
        self.assertEqual(self.preds_info.model_loaded, 1)
        self.assertEqual(self.preds_info.data_loaded, 1)
        self.assertEqual(self.preds_info.ready, 1)

    def test_predict_failed_model(self):
        # Predict using wrong data, should return -2
        self.preds_info.set_model(self.TEST_MODEL)
        self.preds_info.set_data(self.TEST_PREDS)
        self.assertEqual(self.preds_info.predict(10, 256, 18, 1), -2)

    def test_predict_model_wrong_size(self):
        # Predict using wrong data, should return -2
        self.preds_info.set_model(self.TEST_MODEL)
        self.preds_info.set_data(self.TEST_DATA)
        self.assertEqual(self.preds_info.predict(10, 256, 18, 1), -1)

    def test_predict_model_sucess(self):
        # Predict using wrong data, should return -2
        self.preds_info.set_model(self.TEST_MODEL)
        self.preds_info.set_data(self.TEST_DATA)
        self.assertEqual(self.preds_info.predict(self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), 0)

    def test_load_just_data(self):
        # Test loading a model and data
        self.assertEqual(self.preds_info.model_loaded, 0)
        self.assertEqual(self.preds_info.data_loaded, 0)
        self.assertEqual(self.preds_info.ready, 0)
        self.preds_info.set_data(self.TEST_DATA)
        self.assertEqual(self.preds_info.model_loaded, 0)
        self.assertEqual(self.preds_info.data_loaded, 1)
        self.assertEqual(self.preds_info.ready, 0)

    def test_check_preds_shape_binary(self):
        # Check whether preds shape checking works
        # Let's start with binary classification

        # wrong max time
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS,
                                                 2,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong fs
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS,
                                                 self.parent.max_time,
                                                 0.5,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # changing channels shouldn't matter --> not mutli-chn preds
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 2,
                                                 binary=1), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # say its multiclass even though its not --> should work
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 2,
                                                 binary=0), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 1)

    def test_check_preds_shape_mutlichannel(self):
        # Check whether preds shape checking works

        # start with mutlichn
        # correct
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 1)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong max time
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                                 3500,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong fs
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                                 self.parent.max_time,
                                                 0.3,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong number of channels
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 17,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # say its multiclass even though its not --> should work
        # but will set the channels as classes instead
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 2,
                                                 binary=0), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 1)

    def test_check_preds_shape_mutliclass(self):
        # Check whether preds shape checking works

        # start with mutliclass
        # correct
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 1)

        # wrong max time
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 3500,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong fs
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 self.parent.max_time,
                                                 0.3,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong number of channels --> should still work
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 17,
                                                 binary=0), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 1)

        # say its binary even though its not --> should work
        # but will set the classes as channels instead
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 5,
                                                 binary=1), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 1)
        self.assertEqual(self.preds_info.multi_class, 0)

        # but only if nchns matches the number of classes in the file
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

    def test_check_preds_shape_mutliclass_multichn(self):
        # Check whether preds shape checking works

        # start with multiclass, multichn
        # correct
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), 0)
        self.assertEqual(self.preds_info.pred_by_chn, 1)
        self.assertEqual(self.preds_info.multi_class, 1)

        # wrong max time
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN,
                                                 3500,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong fs
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN,
                                                 self.parent.max_time,
                                                 0.3,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=0), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # wrong number of channels
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 17,
                                                 binary=0), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

        # say its binary even though its not
        self.assertEqual(self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN,
                                                 self.parent.max_time,
                                                 self.parent.edf_info.fs,
                                                 self.parent.ci.nchns_to_plot,
                                                 binary=1), -1)
        self.assertEqual(self.preds_info.pred_by_chn, 0)
        self.assertEqual(self.preds_info.multi_class, 0)

    def test_get_color(self):
        # Test the get color function
        ret = self.preds_info.get_color(5)
        self.assertEqual(ret, self.preds_info.class_colors[5])
        ret = self.preds_info.get_color(6)
        self.assertTrue(ret not in self.preds_info.class_colors)

    def test_compute_starts_ends(self):
        # Test the compute starts ends function
        
        # 0) Load in binary predictions
        self.preds_info.set_preds(self.TEST_PREDS, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0, 0, 10,
                        self.parent.edf_info.fs, self.parent.ci.nchns_to_plot)
        self.assertEqual(starts, [768, 2048])
        self.assertEqual(ends, [1024, 2304])
        self.assertEqual(class_vals, [])
        self.assertEqual(chns, [])

        # 1) Load in multi-chn predictions
        self.preds_info.set_preds(self.TEST_PREDS_MULTICHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 0, 10,
                        self.parent.edf_info.fs, self.parent.ci.nchns_to_plot)
        self.assertEqual(starts, [512, 1024])
        self.assertEqual(ends, [1024.0, 1536.0])
        correct_chns = [[False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False,  True, False, False],
                [False, False, False, False, False, False, False, False, False,
                False, False, False, False, False,  True, False, False, False]]
        for x, xx in zip(correct_chns, chns):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)
        self.assertEqual(class_vals, [])

        # 2) Load in multi-class predictions
        self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=0)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 0, 10,
                        self.parent.edf_info.fs, self.parent.ci.nchns_to_plot)
        self.assertEqual(starts, [0.0, 512.0, 1024.0, 1536.0, 2048.0])
        self.assertEqual(ends, [512.0, 1024.0, 1536.0, 2048.0, 2560.0])
        self.assertEqual(chns, [])
        self.assertEqual(class_vals, [0, 2, 2, 4, 0])

        # 3) Load in multi-class multi-chn predictions
        self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=0)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 0, 10,
                        self.parent.edf_info.fs, self.parent.ci.nchns_to_plot)
        self.assertEqual(starts, [0.0, 512.0, 1024.0, 1536.0, 2048.0])
        self.assertEqual(ends, [512.0, 1024.0, 1536.0, 2048.0, 2560.0])
        correct_chns = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        for x, xx in zip(correct_chns, chns):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)

        # 4) Random test case -- chns are less than what is in plot
        self.preds_info.set_preds(self.TEST_PREDS_MULTICHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 0, 10,
                        self.parent.edf_info.fs, 5)
        self.assertEqual(starts, [512, 1024])
        self.assertEqual(ends, [1024.0, 1536.0])
        correct_chns = [[False, False,  True, False, False],
                        [False,  True, False, False, False]]
        for x, xx in zip(correct_chns, chns):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)
        self.assertEqual(class_vals, [])
        
        # 5) Random test case -- chns are less than what is in plot, multiclass
        self.preds_info.set_preds(self.TEST_PREDS_MULTI_CLASS_CHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=0)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 0, 10,
                        self.parent.edf_info.fs, 3)
        self.assertEqual(starts, [0.0, 512.0, 1024.0, 1536.0, 2048.0])
        self.assertEqual(ends, [512.0, 1024.0, 1536.0, 2048.0, 2560.0])
        correct_chns = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        for x, xx in zip(correct_chns, chns):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)

        # 6) Random test case -- make sure nothing breaks if you don't start at 0
        self.preds_info.set_preds(self.TEST_PREDS_MULTICHN, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=1)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 10, 10,
                        self.parent.edf_info.fs, 5)
        self.assertEqual(starts, [4096])
        self.assertEqual(ends, [4608])
        correct_chns = [[False, False, False, False, False]]
        for x, xx in zip(correct_chns, chns):
            for y, yy in zip(x, xx):
                self.assertEqual(y, yy)
        self.assertEqual(class_vals, [])

        # 7) Random test case -- make sure nothing breaks if you don't start at 0
        self.preds_info.set_preds(self.TEST_PREDS_MULTICLASS, self.parent.max_time,
                                  self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
                                  binary=0)
        self.preds_info.preds_to_plot = self.preds_info.preds
        starts, ends, chns, class_vals = self.preds_info.compute_starts_ends_chns(0.5, 20, 10,
                        self.parent.edf_info.fs, self.parent.ci.nchns_to_plot)
        self.assertEqual(starts, [5120.0, 5632.0, 6144.0, 6656.0, 7168.0])
        self.assertEqual(ends, [5632.0, 6144.0, 6656.0, 7168.0, 7680.0])
        self.assertEqual(chns, [])
        self.assertEqual(class_vals, [0, 0, 0, 0, 0])

    def test_invalid_preds_file(self):
        self.assertRaises(Exception, self.preds_info.set_preds, "test.pt", 1, 256, 18)

    def tearDown(self):
        pass

    def _load_signals(self):
        # for loading in the test file
        self.parent.argv.show = 0
        self.parent.argv.fn = self.TEST_FN
        self.parent.load_data(name=self.TEST_FN)
        self.parent.chn_ops.cbox_bip.setChecked(1)
        self.parent.chn_ops.check()
        self.parent.call_initial_move_plot()

if __name__ == '__main__':
    unittest.main(exit=False)