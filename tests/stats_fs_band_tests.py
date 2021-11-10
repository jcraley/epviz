""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from visualization.signal_stats.signalStats_options import SignalStatsOptions
from visualization.signal_stats.signalStats_info import SignalStatsInfo
from visualization.plot import MainPage
from visualization.plot import check_args, get_args

app = QApplication([])
class TestFilter(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "test_files/chb.edf"
        sys.argv = ['visualization/plot.py']
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        self._load_signals()
        self.parent.open_stat_window()
        self.signalstats_info = SignalStatsInfo()
        self.signalstats_info.fs_bands["test0"] = (2, 5)
        self.ui = SignalStatsOptions(self.signalstats_info, self.parent)

    def test_setup(self):
        # Test that everything is checked properly at startup
        self.assertEqual(self.ui.fs_band_count, 1)

    def test_add_fs_band(self):
        # Test adding a fs band
        self.ui.input_name.setText("test1")
        self.ui.input_fs0.setValue(7)
        self.ui.input_fs1.setValue(9)

        self.ui.add_fs_band()

        self.assertEqual(self.ui.fs_band_count, 2)
        self.assertEqual(self.ui.input_name.text(), "")
        self.assertEqual(self.ui.input_fs0.value(), 0)
        self.assertEqual(self.ui.input_fs1.value(), 0)
        
        self.assertEqual(self.signalstats_info.fs_bands["test1"], (7, 9))

    def test_check(self):
        # Test that check adds the new fields to the parent
        fs_band_lbls = self.parent.fs_band_lbls
        orig_keys = ["alpha", "beta", "gamma", "delta", "theta"]
        self.assertEqual(list(fs_band_lbls.keys()).sort(), orig_keys.sort())

        self.ui.check()

        new_keys = orig_keys + ["test0", "test1"]
        self.assertEqual(list(fs_band_lbls.keys()).sort(), new_keys.sort())

    def test_get_power_band_from_sig(self):
        # Test that power bands are computed correctly
        diff_thresh = 0.0000001 # the tolerance for error
        data = self.parent.ci.data_to_plot[0,:]
        lp = 0
        hp = 0
        no_filter_dict = {'delta': 5750580.188063894,
                          'theta': 1623394.1100579707,
                          'alpha': 779765.3023329942,
                          'beta': 69927.60270696628,
                          'gamma': 30319.31786894721,
                          'test0': 3272411.217772229}
        fs_band_dict = self.signalstats_info.get_power(data, 0, 512, hp, lp, self.parent.edf_info.fs)
        for k in no_filter_dict.keys():
            self.assertTrue(abs(no_filter_dict[k] - fs_band_dict[k]) < diff_thresh)
        
        # lp filter on
        lp_filter_dict = {'delta': 5750580.188063894,
                          'theta': 1623394.1100579707,
                          'alpha': 779765.3023329942,
                          'beta': 69927.60270696628,
                          'gamma': 15338.107466774643,
                          'test0': 3272411.217772229}
        lp = 31
        hp = 0
        fs_band_dict = self.signalstats_info.get_power(data, 0, 512, hp, lp, self.parent.edf_info.fs)
        for k in no_filter_dict.keys():
            self.assertTrue(abs(lp_filter_dict[k] - fs_band_dict[k]) < diff_thresh)

        # lp filter on part2
        lp_filter_dict = {'delta': 5750580.188063894,
                          'theta': 1623394.1100579707,
                          'alpha': 779765.3023329942,
                          'beta': 69927.60270696628,
                          'gamma': 0,
                          'test0': 3272411.217772229}
        lp = 30
        hp = 0
        fs_band_dict = self.signalstats_info.get_power(data, 0, 512, hp, lp, self.parent.edf_info.fs)
        for k in no_filter_dict.keys():
            self.assertTrue(abs(lp_filter_dict[k] - fs_band_dict[k]) < diff_thresh)
        
        # hp filter on
        hp_filter_dict = {'delta': 0,
                          'theta': 1256103.6541762687,
                          'alpha': 779765.3023329942,
                          'beta': 69927.60270696628,
                          'gamma': 30319.31786894721,
                          'test0': 0}
        lp = 0
        hp = 6
        fs_band_dict = self.signalstats_info.get_power(data, 0, 512, hp, lp, self.parent.edf_info.fs)
        for k in no_filter_dict.keys():
            self.assertTrue(abs(hp_filter_dict[k] - fs_band_dict[k]) < diff_thresh)
        

        # bp filter on
        bp_filter_dict = {'delta': 0,
                          'theta': 1623394.1100579707,
                          'alpha': 480015.56167355896,
                          'beta': 0,
                          'gamma': 0,
                          'test0': 615836.7259411447}
        lp = 10
        hp = 4
        fs_band_dict = self.signalstats_info.get_power(data, 0, 512, hp, lp, self.parent.edf_info.fs)
        for k in no_filter_dict.keys():
            self.assertTrue(abs(bp_filter_dict[k] - fs_band_dict[k]) < diff_thresh)

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