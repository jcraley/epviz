""" Module for the edf saving window """
from PyQt5.QtWidgets import QWidget

from ui_files.saveEdfOps import Ui_saveToEdf
from edf_saving.anonymizer import Anonymizer

class SaveEdfOptions(QWidget):
    """ Class for the edf saving window """
    def __init__(self,data,parent):
        """ Constructor.

            Args:
                data - the save edf info object holding the patient fields
                parent - the main gui window object
        """
        super().__init__()
        self.data = data
        self.parent = parent
        self.seo_ui = Ui_saveToEdf()
        self.seo_ui.setupUi(self)
        self.setup_ui() # Show the GUI

    def setup_ui(self):
        """ Reset fields """
        self.data.pt_id = "X X X X" + " " * 730
        self.data.rec_info = "Startdate X X X X" + " " * 63
        self.data.start_date = "01.01.01"
        self.data.start_time = "01.01.01"

        self.set_sig_slots()

    def set_sig_slots(self):
        """ set signals and slots """
        self.seo_ui.cbox_orig.toggled.connect(self.cbox_orig_checked)
        self.seo_ui.cbox_anon.toggled.connect(self.cbox_anon_checked)
        self.seo_ui.btn_editFields.clicked.connect(self.open_anon_editor)
        self.seo_ui.btn_anonAndSave.clicked.connect(self.save_and_close)

        self.seo_ui.cbox_anon.setChecked(1)
        if not self.parent.argv.save_edf_fn is None:
            if self.parent.argv.anonymize_edf:
                self.seo_ui.cbox_anon.setChecked(1)
            else:
                self.seo_ui.cbox_anon.setChecked(0)
            self.save_and_close()
        else:
            self.show()

    def cbox_orig_checked(self):
        """ Called when orignal cbox is clicked
        """
        if self.seo_ui.cbox_orig.isChecked():
            self.seo_ui.cbox_anon.setChecked(0)

    def cbox_anon_checked(self):
        """ Called when anonimization cbox is clicked
        """
        if self.seo_ui.cbox_anon.isChecked():
            self.seo_ui.cbox_orig.setChecked(0)

    def open_anon_editor(self):
        """ Opens the anonymization editor and closes this window
        """
        self.parent.anon_win_open = 1
        self.parent.anon_ops = Anonymizer(self.data,self.parent)
        self.close_window()

    def save_and_close(self):
        """ Closes window and calls parent to save edf file
        """
        if self.seo_ui.cbox_orig.isChecked():
            with open(self.data.fn, 'rb') as edf_file:
                file = edf_file.read(200)
            self.data.pt_id = file[8:88].decode("utf-8")
            self.data.rec_info = file[88:168].decode("utf-8")
            self.data.start_date = file[168:176].decode("utf-8")
            self.data.start_time = file[176:184].decode("utf-8")
        self.parent.save_sig_to_edf()
        self.close_window()

    def close_window(self):
        """ Called to close the window """
        self.parent.saveedf_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed. """
        self.parent.saveedf_win_open = 0
        event.accept()
