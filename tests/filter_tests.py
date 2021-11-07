""" Module for testing the filter options window """
import sys
import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from filtering.filter_options import FilterOptions
from filtering.filter_info import FilterInfo
from plot import MainPage
from plot import check_args, get_args
from unittest.mock import patch

app = QApplication([])
class TestFilter(unittest.TestCase):

    def setUp(self):
        sys.argv = ['visualization/plot.py']
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        self.filter_info = FilterInfo()
        # Create a dummy "edf_info" object to hold the fs
        # (doesn't really need to be edf_info, fs is the only thing
        # filter_info needs from edf_info)
        self.parent.edf_info = FilterInfo()
        self.parent.edf_info.fs = 256
        self.filter_info2 = FilterInfo()
        self.filter_info2.do_lp = 0
        self.filter_info2.do_hp = 0
        self.filter_info2.do_bp = 1
        self.filter_info2.do_notch = 1
        self.filter_info2.bp1 = 2
        self.filter_info2.bp1 = 40
        self.filter_info2.notch = 30
        self.ui = FilterOptions(self.filter_info, self.parent)
        self.ui2 = FilterOptions(self.filter_info2, self.parent)

    def test_setup(self):
        # Test that everything is checked properly at startup
        self.assertEqual(self.ui.cbox_lp.isChecked(),1)
        self.assertEqual(self.ui.cbox_hp.isChecked(),1)
        self.assertEqual(self.ui.cbox_notch.isChecked(),0)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)

        self.assertEqual(self.ui2.cbox_lp.isChecked(),0)
        self.assertEqual(self.ui2.cbox_hp.isChecked(),0)
        self.assertEqual(self.ui2.cbox_notch.isChecked(),1)
        self.assertEqual(self.ui2.cbox_bp.isChecked(),1)

    
    def test_click_lp_cbox(self):
        # Test clicking the lp checkbox
        self.ui.cbox_lp.setChecked(0)
        self.assertEqual(self.ui.cbox_lp.isChecked(),0)
        QTest.mouseClick(self.ui.cbox_lp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_lp.isChecked(),1)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        self.assertEqual(self.filter_info.do_lp,1)
        QTest.mouseClick(self.ui.cbox_lp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_lp.isChecked(),0)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        self.assertEqual(self.filter_info.do_lp,0)

    def test_click_hp_cbox(self):
        # Test clicking the hp checkbox
        self.assertEqual(self.ui.cbox_hp.isChecked(),1)
        QTest.mouseClick(self.ui.cbox_hp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_hp.isChecked(),0)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        self.assertEqual(self.filter_info.do_hp,0)
        QTest.mouseClick(self.ui.cbox_hp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_hp.isChecked(),1)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        self.assertEqual(self.filter_info.do_hp,1)

    def test_click_notch_cbox(self):
        # Test clicking the notch checkbox
        self.assertEqual(self.ui.cbox_notch.isChecked(),0)
        QTest.mouseClick(self.ui.cbox_notch, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_hp.isChecked(),1)
        self.assertEqual(self.filter_info.do_notch,1)
        QTest.mouseClick(self.ui.cbox_notch, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_hp.isChecked(),1)
        self.assertEqual(self.filter_info.do_notch,0)
    
    def test_click_bp_cbox(self):
        # Test clicking the bp checkbox
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        QTest.mouseClick(self.ui.cbox_bp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_bp.isChecked(),1)
        self.assertEqual(self.ui.cbox_lp.isChecked(),0)
        self.assertEqual(self.ui.cbox_hp.isChecked(),0)
        self.assertEqual(self.filter_info.do_bp,1)
        QTest.mouseClick(self.ui.cbox_bp, Qt.LeftButton)
        self.assertEqual(self.ui.cbox_bp.isChecked(),0)
        self.assertEqual(self.ui.cbox_lp.isChecked(),0)
        self.assertEqual(self.ui.cbox_hp.isChecked(),0)
        self.assertEqual(self.filter_info.do_bp,0)

    def test_click_exit_test0(self):
        # Test clicking the ok button and that the FilterInfo object
        # is updated properly
        # assert that FilterInfo object is correct before change
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
        # set some new values
        self.ui.btn_get_lp.setValue(20)
        self.ui.btn_get_hp.setValue(10)
        self.ui.btn_get_notch.setValue(0)
        self.ui.cbox_hp.setChecked(0)
        self.ui.cbox_lp.setChecked(1)
        # click the button and check for updates
        QTest.mouseClick(self.ui.btn_exit, Qt.LeftButton)
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 20)
        self.assertEqual(self.filter_info.notch, 60)

    def test_click_exit_test1(self):
        # Test clicking the ok button and that the FilterInfo object
        # is updated properly
        # assert that FilterInfo object is correct before change
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
        # set some new values
        self.ui.btn_get_lp.setValue(10)
        self.ui.btn_get_hp.setValue(10)
        self.ui.cbox_hp.setChecked(1)
        self.ui.cbox_lp.setChecked(0)
        # click the button and check for updates
        QTest.mouseClick(self.ui.btn_exit, Qt.LeftButton)
        self.assertEqual(self.filter_info.hp, 10)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
    
    def test_click_exit_test2(self):
        # Test clicking the ok button and that the FilterInfo object
        # is updated properly
        # assert that FilterInfo object is correct before change
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
        # set some new values
        self.ui.btn_get_lp.setValue(20)
        self.ui.btn_get_hp.setValue(10)
        self.ui.cbox_hp.setChecked(1)
        self.ui.cbox_lp.setChecked(1)
        # click the button and check for updates
        QTest.mouseClick(self.ui.btn_exit, Qt.LeftButton)
        self.assertEqual(self.filter_info.hp, 10)
        self.assertEqual(self.filter_info.lp, 20)
        self.assertEqual(self.filter_info.notch, 60)

    def test_click_exit_test3(self):
        # Test clicking the ok button and that the FilterInfo object
        # is updated properly
        # assert that FilterInfo object is correct before change
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
        self.assertEqual(self.filter_info.bp1, 0)
        self.assertEqual(self.filter_info.bp2, 0)
        # set some new values
        self.ui.cbox_hp.setChecked(0)
        self.ui.cbox_lp.setChecked(0)
        self.ui.cbox_bp.setChecked(1)
        self.ui.cbox_notch.setChecked(1)
        self.ui.btn_get_notch.setValue(20)
        self.ui.btn_get_bp1.setValue(1)
        self.ui.btn_get_bp2.setValue(30)
        # click the button and check for updates
        QTest.mouseClick(self.ui.btn_exit, Qt.LeftButton)
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 20)
        self.assertEqual(self.filter_info.bp1, 1)
        self.assertEqual(self.filter_info.bp2, 30)

    def test_click_exit_invalid_params(self):
        # Make sure that if something is set inproperly it does not
        # persist in the FilterInfo object
        # assert that FilterInfo object is correct before change
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)
        # set some new values
        self.ui.btn_get_lp.setValue(200)
        self.ui.btn_get_hp.setValue(10)
        self.ui.cbox_hp.setChecked(0)
        self.ui.cbox_lp.setChecked(1)
        # click the button and check for updates
        QTest.mouseClick(self.ui.btn_exit, Qt.LeftButton)
        self.assertEqual(self.filter_info.hp, 2)
        self.assertEqual(self.filter_info.lp, 30)
        self.assertEqual(self.filter_info.notch, 60)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
