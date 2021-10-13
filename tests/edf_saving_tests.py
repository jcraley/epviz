""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from visualization.edf_saving.saveEdf_options import SaveEdfOptions
from visualization.edf_saving.saveEdf_info import SaveEdfInfo
from visualization.edf_saving.anonymizer import Anonymizer, _valid_date
from visualization.plot import MainPage
from visualization.plot import check_args, get_args
from unittest.mock import patch

import datetime

app = QApplication([])
class TestEdfSaving(unittest.TestCase):
    def setUp(self):
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/E_B_1-DeID_0003.edf"
        self.TEST_SAVE_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/test0.edf"
        patch('sys.argv', ["--show","0"])
        args = get_args()
        check_args(args)
        self.parent = MainPage(args, app)
        # self.parent.argv.save_edf_fn = "/Users/daniellecurrey/Desktop/test0.edf"
        # self._load_signals()
        self.saveedf_info = SaveEdfInfo()
        self.saveedf_info.fn =self.TEST_FN
        self.ui = SaveEdfOptions(self.saveedf_info, self.parent)

    def test_setup(self):
        # Test that everything is checked properly at startup
        self.assertEqual(self.saveedf_info.pt_id, "X X X X" + " " * 73)
        self.assertEqual(self.saveedf_info.rec_info, "Startdate X X X X" + " " * 63)
        self.assertEqual(self.saveedf_info.start_date, "01.01.01")
        self.assertEqual(self.saveedf_info.start_time, "01.01.01")
    
    def test_setup_with_edf_fn(self):
        # Test with edf file to save + anon
        self.parent.argv.save_edf_fn = self.TEST_SAVE_FN
        saveedf_info2 = SaveEdfInfo()
        saveedf_info2.fn =self.TEST_FN
        ui2 = SaveEdfOptions(saveedf_info2, self.parent)
        self.assertTrue(ui2.seo_ui.cbox_anon.isChecked())

    def test_setup_with_edf_fn_orig(self):
        # Test with edf file to save + anon
        self.parent.argv.save_edf_fn = self.TEST_SAVE_FN
        self.parent.argv.anonymize_edf = 0
        saveedf_info2 = SaveEdfInfo()
        saveedf_info2.fn =self.TEST_FN
        ui2 = SaveEdfOptions(saveedf_info2, self.parent)
        self.assertTrue(ui2.seo_ui.cbox_orig.isChecked())

    def test_cboxes(self):
        # Test that cboxes work properly
        self.assertEqual(self.ui.seo_ui.cbox_anon.isChecked(), 1)
        QTest.mouseClick(self.ui.seo_ui.cbox_orig, Qt.LeftButton)
        self.assertEqual(self.ui.seo_ui.cbox_anon.isChecked(), 0)
        self.assertEqual(self.ui.seo_ui.cbox_orig.isChecked(), 1)
        QTest.mouseClick(self.ui.seo_ui.cbox_anon, Qt.LeftButton)
        self.assertEqual(self.ui.seo_ui.cbox_anon.isChecked(), 1)
        self.assertEqual(self.ui.seo_ui.cbox_orig.isChecked(), 0)

    def test_open_ann_editor(self):
        # Test that cboxes work properly
        self.assertEqual(self.parent.anon_win_open, 0)
        self.ui.open_anon_editor()
        self.assertEqual(self.parent.anon_win_open, 1)

    def test_save_to_edf(self):
        # Test saving to edf with anonymization
        self.ui.save_and_close()
        self.assertEqual(self.saveedf_info.pt_id, "X X X X" + " " * 73)
        self.assertEqual(self.saveedf_info.rec_info, "Startdate X X X X" + " " * 63)
        self.assertEqual(self.saveedf_info.start_date, "01.01.01")
        self.assertEqual(self.saveedf_info.start_time, "01.01.01")

    def test_save_to_edf_keep_current_fields(self):
        # Test saving to edf without anonymization
        self.ui.seo_ui.cbox_orig.setChecked(1)
        self.ui.save_and_close()

        with open(self.saveedf_info.fn, 'rb') as edf_file:
            file = edf_file.read(200)
            self.assertEqual(self.saveedf_info.pt_id, file[8:88].decode("utf-8"))
            self.assertEqual(self.saveedf_info.rec_info, file[88:168].decode("utf-8"))
            self.assertEqual(self.saveedf_info.start_date, file[168:176].decode("utf-8"))
            self.assertEqual(self.saveedf_info.start_time, file[176:184].decode("utf-8"))

    def test_convert_to_header(self):
        # Test converting string fields to header dict
        self.saveedf_info.pt_id = "1234 F 17-DEC-2002 Jane_Doe EPviz Is Awesome"
        self.saveedf_info.rec_info = "Startdate X 007 DC jhu_eeg_1234"
        self.saveedf_info.start_date = "27.05.21"
        self.saveedf_info.start_time = "19.00.00"

        dict_vals = {'technician': 'DC',
                     'recording_additional': '',
                     'patientname': 'Jane_Doe',
                     'patient_additional': 'EPvizIsAwesome',
                     'patientcode': '1234',
                     'equipment': 'jhu_eeg_1234',
                     'admincode': '007',
                     'gender': 'F',
                     'startdate': datetime.datetime(2021, 5, 27, 19, 0, 0),
                     'birthdate': datetime.datetime(2002, 12, 17, 0, 0, 0)}
        
        self.saveedf_info.convert_to_header()

        for k in dict_vals:
            self.assertEqual(dict_vals[k], self.saveedf_info.pyedf_header[k])
        
        self.saveedf_info.pyedf_header = {'technician': '002', 'recording_additional': '', 'patientname': '',
                        'patient_additional': '', 'patientcode': '', 'equipment': '',
                        'admincode': '', 'gender': '',
                        'startdate': datetime.datetime(2001, 1, 1, 1, 1, 1),
                        'birthdate': ''}

        self.saveedf_info.pt_id = "1234 F X Jane_Doe"
        self.saveedf_info.rec_info = "Startdate X 007 DC jhu_eeg_1234 Some Extra Cool Words"
        self.saveedf_info.start_date = "27.05.98"
        self.saveedf_info.start_time = "19.00.00"

        dict_vals = {'technician': 'DC',
                     'recording_additional': 'SomeExtraCoolWords',
                     'patientname': 'Jane_Doe',
                     'patient_additional': '',
                     'patientcode': '1234',
                     'equipment': 'jhu_eeg_1234',
                     'admincode': '007',
                     'gender': 'F',
                     'startdate': datetime.datetime(1998, 5, 27, 19, 0, 0),
                     'birthdate': ""}
        
        self.saveedf_info.convert_to_header()

        for k in dict_vals:
            self.assertEqual(dict_vals[k], self.saveedf_info.pyedf_header[k])

    def test_anonymizer_setup(self):
        # Test the setup of the anonymizer
        MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP",
                    "OCT","NOV","DEC"]
        self.anon_ui = Anonymizer(self.saveedf_info, self.parent)
        with open(self.saveedf_info.fn, 'rb') as f:
            file = f.read(200)
        file = bytearray(file)
        pt_id_text = file[8:88].decode("utf-8").split(" ")
        rec_info_text = file[88:168].decode("utf-8").split(" ")
        print(file)
        self.assertEqual(self.anon_ui.lbl_fn.text(), "E_B_1-DeID_0003...")
        self.assertEqual(self.anon_ui.btn_anonfile.isEnabled(), 1)
        self.assertEqual(self.anon_ui.cbox_copyoriginal.isEnabled(), 1)
        self.assertEqual(self.anon_ui.cbox_setdefaults.isEnabled(), 1)
        self.assertEqual(self.anon_ui.cbox_setdefaults.isChecked(), 1)
        for i in range(len(self.anon_ui.pt_id_fields)):
            self.assertEqual(self.anon_ui.pt_id_fields[i].isEnabled(), 1)
        for i in range(len(self.anon_ui.rec_info_fields)):
            self.assertEqual(self.anon_ui.rec_info_fields[i].isEnabled(), 1)
        for i in range(len(self.anon_ui.date_time_lbls)):
            self.assertEqual(self.anon_ui.datetimefield_inputs[i].isEnabled(), 1)
        
        self.assertEqual(self.anon_ui.oldpt_id_fields[0].text(), pt_id_text[0])
        self.assertEqual(self.anon_ui.radio_pt_id_x2.isChecked(), 1)
        self.assertEqual(self.anon_ui.radio_pt_id_date2.isChecked(), 1)
        self.assertEqual(self.anon_ui.dob.date().year(), int(pt_id_text[2].split("-")[2]))
        self.assertEqual(self.anon_ui.dob.date().month(), MONTHS.index(pt_id_text[2].split("-")[1]) + 1)
        self.assertEqual(self.anon_ui.dob.date().day(), int(pt_id_text[2].split("-")[0]))

        self.assertEqual(self.anon_ui.oldpt_id_fields[3].text(), pt_id_text[3])
        self.assertEqual(self.anon_ui.oldpt_id_fields[4].text(), "")

        self.assertEqual(self.anon_ui.rec_info_date2.isChecked(), 1)
        self.assertEqual(self.anon_ui.startdate.date().year(), int(rec_info_text[1].split("-")[2]))
        self.assertEqual(self.anon_ui.startdate.date().month(), MONTHS.index(rec_info_text[1].split("-")[1]) + 1)
        self.assertEqual(self.anon_ui.startdate.date().day(), int(rec_info_text[1].split("-")[0]))
        self.assertEqual(self.anon_ui.oldrec_info_fields[1].text(), rec_info_text[2])
        self.assertEqual(self.anon_ui.oldrec_info_fields[2].text(), rec_info_text[3])
        self.assertEqual(self.anon_ui.oldrec_info_fields[3].text(), rec_info_text[4])
        self.assertEqual(self.anon_ui.oldrec_info_fields[4].text(), "")

        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().year(), 2001)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().month(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().day(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().hour(), 4)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().minute(), 22)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().second(), 0)     
    
    def test_copy_original_anon(self):
        # Test clicking anon cboxes
        self.anon_ui = Anonymizer(self.saveedf_info, self.parent)
        self.assertEqual(self.anon_ui.cbox_copyoriginal.isChecked(), 0)
        self.assertEqual(self.anon_ui.cbox_setdefaults.isChecked(), 1)

        self.assertEqual(self.anon_ui.pt_id_fields[0].text(), "X")
        self.assertEqual(self.anon_ui.radio_pt_id_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.radio_pt_id_date_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.pt_id_fields[3].text(), "X")
        self.assertEqual(self.anon_ui.pt_id_fields[4].text(), "")

        self.assertEqual(self.anon_ui.rec_info_date_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.rec_info_fields[1].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[2].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[3].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[4].text(), "")

        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().year(), 2001)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().month(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().day(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().hour(), 4)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().minute(), 22)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().second(), 0)

        QTest.mouseClick(self.anon_ui.cbox_copyoriginal, Qt.LeftButton)
        self.assertEqual(self.anon_ui.cbox_copyoriginal.isChecked(), 1)
        self.assertEqual(self.anon_ui.cbox_setdefaults.isChecked(), 0)

        self.assertEqual(self.anon_ui.pt_id_fields[0].text(), self.anon_ui.oldpt_id_fields[0].text())
        self.assertTrue(self.anon_ui.radio_pt_id_x.isChecked())
        self.assertTrue(self.anon_ui.radio_pt_id_date.isChecked())

        self.assertEqual(self.anon_ui.dobedit.date(), self.anon_ui.dob.date())
        self.assertEqual(self.anon_ui.pt_id_fields[3].text(), self.anon_ui.oldpt_id_fields[3].text())
        self.assertEqual(self.anon_ui.pt_id_fields[4].text(), self.anon_ui.oldpt_id_fields[4].text())

        self.assertTrue(self.anon_ui.rec_info_date.isChecked())

        self.assertEqual(self.anon_ui.startdateedit.date(), self.anon_ui.startdate.date())
        self.assertEqual(self.anon_ui.rec_info_fields[1].text(), self.anon_ui.oldrec_info_fields[1].text())
        self.assertEqual(self.anon_ui.rec_info_fields[2].text(), self.anon_ui.oldrec_info_fields[2].text())
        self.assertEqual(self.anon_ui.rec_info_fields[3].text(), self.anon_ui.oldrec_info_fields[3].text())
        self.assertEqual(self.anon_ui.rec_info_fields[4].text(), self.anon_ui.oldrec_info_fields[4].text())

        self.assertEqual(self.anon_ui.datetimefield_inputs[0].date(), self.anon_ui.olddatetimefield_inputs[0].date())
        self.assertEqual(self.anon_ui.datetimefield_inputs[1].time(), self.anon_ui.olddatetimefield_inputs[1].time())

        QTest.mouseClick(self.anon_ui.cbox_setdefaults, Qt.LeftButton)
        self.assertEqual(self.anon_ui.cbox_copyoriginal.isChecked(), 0)
        self.assertEqual(self.anon_ui.cbox_setdefaults.isChecked(), 1)

        self.assertEqual(self.anon_ui.pt_id_fields[0].text(), "X")
        self.assertEqual(self.anon_ui.radio_pt_id_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.radio_pt_id_date_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.pt_id_fields[3].text(), "X")
        self.assertEqual(self.anon_ui.pt_id_fields[4].text(), "")

        self.assertEqual(self.anon_ui.rec_info_date_x.isChecked(), 1)
        self.assertEqual(self.anon_ui.rec_info_fields[1].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[2].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[3].text(), "X")
        self.assertEqual(self.anon_ui.rec_info_fields[4].text(), "")

        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().year(), 2001)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().month(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[0].date().day(), 1)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().hour(), 4)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().minute(), 22)
        self.assertEqual(self.anon_ui.olddatetimefield_inputs[1].time().second(), 0)
    
    def test_valid_date(self):
        # Test the _valid_date function in anonymize
        self.assertEqual(-1, _valid_date("abcdefg"))
        self.assertEqual(-1, _valid_date("01-JAN-01"))
        self.assertEqual(-1, _valid_date("01-ABC-2001"))
        self.assertEqual(-1, _valid_date("1-JAN-2001"))
        self.assertEqual(-1, _valid_date("AB-JAN-2001"))
        self.assertEqual(-1, _valid_date("01-JAN-200C"))
        self.assertEqual(0, _valid_date("01-JAN-2001"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)