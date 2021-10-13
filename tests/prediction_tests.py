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

import datetime

app = QApplication([])
class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/chb01_03.edf"
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