""" Module for the anonymizer window """
from PyQt5.QtCore import Qt, QTime, QDate

from PyQt5.QtWidgets import (QMessageBox, QWidget, QPushButton, QLabel,
                             QGridLayout, QLineEdit, QTimeEdit, QFrame,
                             QDateEdit, QGroupBox, QRadioButton, QHBoxLayout,
                             QCheckBox)
from PyQt5.QtGui import QFont
from matplotlib.backends.qt_compat import QtWidgets

class Anonymizer(QWidget):
    """ Class for the anonymizer window """
    def __init__(self, data, parent):
        """ Constructor.

            Args:
                data - the save edf info object holding the patient fields
                parent - the main gui window object
        """
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'EDF Anonymizer'
        size_object = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width = size_object.width() * 0.2
        self.height = size_object.height() * 0.2
        self.field_defaults = [bytes(" " * 80, 'utf-8'), bytes(" " * 80, 'utf-8'),
                                bytes("01.01.01", 'utf-8'), bytes("01.01.01", 'utf-8')]

        self.data = data
        self.parent = parent

        self.MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP",
                        "OCT","NOV","DEC"]

        self.init_ui()

    def init_ui(self):
        """ Setup the UI
        """
        layout = QGridLayout()

        font = QFont()
        font.setPointSize(16)
        lbl_info = QLabel("Update fields and click anonymize " +
                        "and save to select location for new file.")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setFont(font)
        layout.addWidget(lbl_info,0,0,1,3)

        # ---- Add in all subfields ---- #
        pt_id_rec_info_fields = QGridLayout()

        lbloriginal = QLabel("Original")
        lbloriginal.setAlignment(Qt.AlignCenter)
        pt_id_rec_info_fields.addWidget(lbloriginal,0,2)
        lblnew = QLabel("Modified")
        lblnew.setAlignment(Qt.AlignCenter)
        pt_id_rec_info_fields.addWidget(lblnew,0,3)
        self.cbox_copyoriginal = QCheckBox("Copy original values")
        self.cbox_copyoriginal.setEnabled(0)
        pt_id_rec_info_fields.addWidget(self.cbox_copyoriginal,1,3)
        self.cbox_setdefaults = QCheckBox("Set default values")
        self.cbox_setdefaults.setEnabled(0)
        pt_id_rec_info_fields.addWidget(self.cbox_setdefaults,2,3)

        lbl_pt_id = QLabel("Patient ID:")
        pt_id_rec_info_fields.addWidget(lbl_pt_id,3,0,5,1)
        lbl_rec_info = QLabel("Recording information:")
        pt_id_rec_info_fields.addWidget(lbl_rec_info,8,0,5,1)

        lblhospcode = QLabel("Hospital code:")
        lblsex = QLabel("Sex:")
        lbldob = QLabel("Date of birth:")
        lblptname = QLabel("Patient name:")
        lblother = QLabel("Other:")
        self.pt_id_lbls = [lblhospcode, lblsex, lbldob, lblptname,lblother]
        hospcodeedit = QLineEdit()
        groupbox_sex_edit = QGroupBox()
        self.radio_pt_id_f = QRadioButton("F")
        self.radio_pt_id_m = QRadioButton("M")
        self.radio_pt_id_x = QRadioButton("X")
        self.radio_pt_id_x.setChecked(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.radio_pt_id_f)
        hbox.addWidget(self.radio_pt_id_m)
        hbox.addWidget(self.radio_pt_id_x)
        groupbox_sex_edit.setLayout(hbox)
        groupbox_date_edit = QGroupBox()
        self.radio_pt_id_date = QRadioButton("")
        self.radio_pt_id_date_x = QRadioButton("X")
        self.radio_pt_id_date_x.setChecked(True)
        self.dobedit = QDateEdit(QDate(2001, 1, 1))
        self.dobedit.setDisplayFormat("MM/dd/yyyy")
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.radio_pt_id_date)
        hbox2.addWidget(self.dobedit)
        hbox2.addWidget(self.radio_pt_id_date_x)
        groupbox_date_edit.setLayout(hbox2)
        ptnameedit = QLineEdit()
        ptidotheredit = QLineEdit()
        self.pt_id_fields = [hospcodeedit,
                             groupbox_sex_edit,
                             groupbox_date_edit,
                             ptnameedit,
                             ptidotheredit]
        hospcode = QLineEdit()
        groupbox_sex = QGroupBox()
        self.radio_pt_id_f2 = QRadioButton("F")
        self.radio_pt_id_m2 = QRadioButton("M")
        self.radio_pt_id_x2 = QRadioButton("X")
        self.radio_pt_id_f2.setChecked(True)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.radio_pt_id_f2)
        hbox3.addWidget(self.radio_pt_id_m2)
        hbox3.addWidget(self.radio_pt_id_x2)
        groupbox_sex.setLayout(hbox3)
        groupbox_date = QGroupBox()
        self.radio_pt_id_date2 = QRadioButton("")
        self.radio_pt_id_date_x2 = QRadioButton("X")
        self.radio_pt_id_date2.setChecked(True)
        self.dob = QDateEdit(QDate(2001, 1, 1))
        self.dob.setDisplayFormat("MM/dd/yyyy")
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.radio_pt_id_date2)
        hbox4.addWidget(self.dob)
        hbox4.addWidget(self.radio_pt_id_date_x2)
        groupbox_date.setLayout(hbox4)
        ptname = QLineEdit()
        ptidother = QLineEdit()
        self.oldpt_id_fields = [hospcode,groupbox_sex,groupbox_date,ptname,ptidother]

        for i,l in enumerate(self.pt_id_lbls):
            pt_id_rec_info_fields.addWidget(l,i + 3,1)
            pt_id_rec_info_fields.addWidget(self.oldpt_id_fields[i],i + 3,2)
            pt_id_rec_info_fields.addWidget(self.pt_id_fields[i],i + 3,3)
            self.oldpt_id_fields[i].setDisabled(1)
            self.pt_id_fields[i].setDisabled(1)

        pt_id_rec_info_fields.addWidget(QHLine(), len(self.pt_id_lbls) + 3, 0, 1, 4)

        lblstartdate = QLabel("Startdate:")
        lblhospadmincode = QLabel("Hospital admin code:")
        lbltechcode = QLabel("Technician code:")
        lblequip = QLabel("Equipment code:")
        lblother = QLabel("Other:")
        self.rec_info_lbls = [lblstartdate, lblhospadmincode, lbltechcode, lblequip, lblother]
        groupbox_date_editrec_info = QGroupBox()
        self.rec_info_date = QRadioButton("")
        self.rec_info_date_x = QRadioButton("X")
        self.rec_info_date_x.setChecked(True)
        self.startdateedit = QDateEdit(QDate(2001, 1, 1))
        self.startdateedit.setDisplayFormat("MM/dd/yyyy")
        hb = QHBoxLayout()
        hb.addWidget(self.rec_info_date)
        hb.addWidget(self.startdateedit)
        hb.addWidget(self.rec_info_date_x)
        groupbox_date_editrec_info.setLayout(hb)
        hospadmincodeedit = QLineEdit()
        techcodeedit = QLineEdit()
        equipcodeedit = QLineEdit()
        recinfootheredit = QLineEdit()
        self.rec_info_fields = [groupbox_date_editrec_info,
                                hospadmincodeedit,
                                techcodeedit,
                                equipcodeedit,
                                recinfootheredit]
        groupbox_daterec_info = QGroupBox()
        self.rec_info_date2 = QRadioButton("")
        self.rec_info_date_x2 = QRadioButton("X")
        self.rec_info_date2.setChecked(True)
        self.startdate = QDateEdit(QDate(2001, 1, 1))
        self.startdate.setDisplayFormat("MM/dd/yyyy")
        hb = QHBoxLayout()
        hb.addWidget(self.rec_info_date2)
        hb.addWidget(self.startdate)
        hb.addWidget(self.rec_info_date_x2)
        groupbox_daterec_info.setLayout(hb)
        hospadmincode = QLineEdit()
        techcode = QLineEdit()
        equipcode = QLineEdit()
        recinfoother = QLineEdit()
        self.oldrec_info_fields = [groupbox_daterec_info,
                                   hospadmincode,
                                   techcode,
                                   equipcode,
                                   recinfoother]
        for i,l in enumerate(self.rec_info_lbls):
            pt_id_rec_info_fields.addWidget(l,
                    i + len(self.oldpt_id_fields) + 4,1)
            pt_id_rec_info_fields.addWidget(self.oldrec_info_fields[i],
                    i + len(self.oldpt_id_fields) + 4,2)
            pt_id_rec_info_fields.addWidget(self.rec_info_fields[i],
                    i + len(self.oldpt_id_fields) + 4,3)
            self.rec_info_fields[i].setDisabled(1)
            self.oldrec_info_fields[i].setDisabled(1)

        pt_id_rec_info_fields.addWidget(QHLine(), len(self.pt_id_lbls) +
                        len(self.oldpt_id_fields) + 4, 0, 1, 4)
        layout.addLayout(pt_id_rec_info_fields, 3, 0, 1,3)

        lbl_start_date = QLabel("Start date:")
        lbl_start_time = QLabel("Start time:")
        oldinput_start_date = QDateEdit(QDate(2001, 1, 1))
        oldinput_start_date.setDisplayFormat("MM/dd/yyyy")
        oldinput_start_time = QTimeEdit(QTime(1, 1, 1))
        oldinput_start_time.setDisplayFormat("hh:mm:ss")
        inputStartDate = QDateEdit(QDate(2001, 1, 1))
        inputStartDate.setDisplayFormat("MM/dd/yyyy")
        inputStartTime = QTimeEdit(QTime(1, 1, 1))
        inputStartTime.setDisplayFormat("hh:mm:ss")

        self.date_time_lbls = [lbl_start_date,lbl_start_time]
        self.olddatetimefield_inputs = [oldinput_start_date,oldinput_start_time]
        self.datetimefield_inputs = [inputStartDate,inputStartTime]
        for i,l in enumerate(self.date_time_lbls):
            pt_id_rec_info_fields.addWidget(l,i + len(self.oldpt_id_fields) +
                            len(self.pt_id_lbls) + 6,1)
            self.olddatetimefield_inputs[i].setDisabled(1)
            self.datetimefield_inputs[i].setDisabled(1)
            pt_id_rec_info_fields.addWidget(self.olddatetimefield_inputs[i],i +
                    len(self.oldpt_id_fields) + len(self.pt_id_lbls) + 6,2)
            pt_id_rec_info_fields.addWidget(self.datetimefield_inputs[i],i +
                    len(self.oldpt_id_fields) + len(self.pt_id_lbls) + 6,3)

        # Set defaults
        self.pt_id_fields[0].setText("X")

        self.pt_id_fields[3].setText("X")
        self.pt_id_fields[4].setText("")

        self.rec_info_fields[1].setText("X")
        self.rec_info_fields[2].setText("X")
        self.rec_info_fields[3].setText("X")
        self.rec_info_fields[4].setText("")

        # ---- -------------------- ---- #

        self.lbl_fn = QLabel("No file loaded.")
        self.lbl_fn.setFont(font)
        layout.addWidget(self.lbl_fn,1,1,1,1)
        layout.addWidget(QHLine(), 2, 0, 1, 3)

        layout.addWidget(QHLine(), len(self.date_time_lbls) + 5, 0, 1, 3)
        self.btn_anonfile = QPushButton("Anonymize and save file",self)
        layout.addWidget(self.btn_anonfile,len(self.date_time_lbls) + 6,0,1,3)
        self.btn_anonfile.setDisabled(True)

        self.setWindowTitle(self.title)
        self.setLayout(layout)

        self.set_signals_slots()
        self.show()

    def set_signals_slots(self):
        """ Set up the signals and slots.
        """
        self.btn_anonfile.clicked.connect(self.anon_file)
        self.cbox_copyoriginal.toggled.connect(self.copy_original)
        self.cbox_setdefaults.toggled.connect(self.set_defaults)
        self.load_file()

    def load_file(self):
        """ Function to populate fields with the info from the edf header
        """
        name = self.data.fn
        self.input_fn = name
        self.input_fn_text = name.split('/')[-1]
        if len(name.split('/')[-1]) > 15:
            self.input_fn_text = name.split('/')[-1][0:15] + "..."
        self.lbl_fn.setText(self.input_fn_text)
        self.btn_anonfile.setDisabled(0)
        self.cbox_copyoriginal.setEnabled(1)
        self.cbox_setdefaults.setEnabled(1)
        self.cbox_setdefaults.setChecked(1)
        # Setup all fields to anonymize
        for i in range(len(self.pt_id_fields)):
            self.pt_id_fields[i].setDisabled(0)
        for i in range(len(self.rec_info_fields)):
            self.rec_info_fields[i].setDisabled(0)
        for i in range(len(self.date_time_lbls)):
            self.datetimefield_inputs[i].setDisabled(0)
        # Open the file
        with open(self.input_fn, 'rb') as f:
            file = f.read(200)
        file = bytearray(file)
        pt_id_text = file[8:88].decode("utf-8").split(" ")
        rec_info_text = file[88:168].decode("utf-8").split(" ")
        # Error checking
        if len(pt_id_text) > 1:
            if not (pt_id_text[1] in {"X","F","M"}):
                pt_id_text[1] = "X"
            if len(pt_id_text) > 2:
                if self._valid_date(pt_id_text[2]) == -1:
                    pt_id_text[2] = "01-JAN-2001"
        if len(pt_id_text) == 0:
            pt_id_text = ["X","X","01-JAN-2001","X"]
        elif len(pt_id_text) == 1:
            pt_id_text.append("X")
            pt_id_text.append("01-JAN-2001")
            pt_id_text.append("X")
        elif len(pt_id_text) == 2:
            pt_id_text.append("01-JAN-2001")
            pt_id_text.append("X")
        elif len(pt_id_text) == 3:
            pt_id_text.append("X")
        elif len(pt_id_text) >= 4:
            if pt_id_text[0] == " " or pt_id_text[0] == "":
                pt_id_text[0] = "X"
            if pt_id_text[3] == " " or pt_id_text[3] == "":
                pt_id_text[3] = "X"

        if len(rec_info_text) > 1:
            if self._valid_date(rec_info_text[1]) == -1:
                rec_info_text[1] = "01-JAN-2001"
        if len(rec_info_text) == 0:
            rec_info_text = ["Startdate","01-JAN-2001","X","X","X"]
        elif len(rec_info_text) == 1:
            rec_info_text.append("01-JAN-2001")
            rec_info_text.append("X")
            rec_info_text.append("X")
            rec_info_text.append("X")
        elif len(rec_info_text) == 2:
            rec_info_text.append("X")
            rec_info_text.append("X")
            rec_info_text.append("X")
        elif len(rec_info_text) == 3:
            rec_info_text.append("X")
            rec_info_text.append("X")
        elif len(rec_info_text) == 4:
            rec_info_text.append("X")
        elif len(rec_info_text) >= 5:
            if rec_info_text[2] == " " or rec_info_text[2] == "":
                rec_info_text[2] = "X"
            if rec_info_text[3] == " " or rec_info_text[3] == "":
                rec_info_text[3] = "X"
            if rec_info_text[4] == " " or rec_info_text[4] == "":
                rec_info_text[4] = "X"
        self.oldpt_id_fields[0].setText(pt_id_text[0])
        if pt_id_text[1] == "F":
            self.radio_pt_id_f2.setChecked(1)
        elif pt_id_text[1] == "M":
            self.radio_pt_id_m2.setChecked(1)
        else:
            self.radio_pt_id_x2.setChecked(1)
        if pt_id_text[2] == "X":
            self.radio_pt_id_date_x2.setChecked(1)
        else:
            self.radio_pt_id_date2.setChecked(1)
            yr = int(pt_id_text[2].split("-")[2])
            mth = self.MONTHS.index(pt_id_text[2].split("-")[1]) + 1
            day = int(pt_id_text[2].split("-")[0])
            self.dob.setDate(QDate(yr,mth,day))
        self.oldpt_id_fields[3].setText(pt_id_text[3])
        if len(pt_id_text) > 4:
            self.oldpt_id_fields[4].setText("".join(pt_id_text[4:]))
        else:
            self.oldpt_id_fields[4].setText("")

        if rec_info_text[1] == "X":
            self.rec_info_date_x2.setChecked(1)
        else:
            self.rec_info_date2.setChecked(1)
            yr = int(rec_info_text[1].split("-")[2])
            mth = self.MONTHS.index(rec_info_text[1].split("-")[1]) + 1
            day = int(rec_info_text[1].split("-")[0])
            self.startdate.setDate(QDate(yr,mth,day))
        self.oldrec_info_fields[1].setText(rec_info_text[2])
        self.oldrec_info_fields[2].setText(rec_info_text[3])
        self.oldrec_info_fields[3].setText(rec_info_text[4])
        if len(rec_info_text) > 5:
            self.oldrec_info_fields[4].setText("".join(rec_info_text[5:]))
        else:
            self.oldrec_info_fields[4].setText("")

        yrs = int(file[174:176].decode("utf-8"))
        if yrs > 20:
            yrs = yrs + 1900
        else:
            yrs = yrs + 2000
        mths = int(file[171:173].decode("utf-8"))
        dys = int(file[168:170].decode("utf-8"))
        hrs = int(file[176:178].decode("utf-8"))
        minutes = int(file[179:181].decode("utf-8"))
        sec = int(file[182:184].decode("utf-8"))
        self.olddatetimefield_inputs[0].setDate(QDate(yrs,mths,dys))
        self.olddatetimefield_inputs[1].setTime(QTime(hrs,minutes,sec))

    def anon_file(self):
        """ Saves anonymized fields and closes window.
        """
        # Get info from user
        pt_id = ""
        rec_info = ""
        start_time = ""
        start_date = self.datetimefield_inputs[0].date().toString("dd.MM.yy")
        start_time = self.datetimefield_inputs[1].time().toString("hh.mm.ss")

        if self.radio_pt_id_f.isChecked():
            sex = "F"
        elif self.radio_pt_id_m.isChecked():
            sex = "M"
        else:
            sex = "X"
        if self.radio_pt_id_date_x.isChecked():
            pt_id_date = "X"
        else:
            pt_id_date = self.dobedit.date().toString("dd-MMM-yyyy").upper()

        if self.pt_id_fields[0].text() == "" or self.pt_id_fields[0].text() == " ":
            self.pt_id_fields[0].setText("X")
        if self.pt_id_fields[3].text() == "" or self.pt_id_fields[3].text() == " ":
            self.pt_id_fields[3].setText("X")

        pt_id = (self.pt_id_fields[0].text().replace(" ","_") + " " + sex + " " +
                pt_id_date + " " + self.pt_id_fields[3].text().replace(" ","_") + " " +
                self.pt_id_fields[4].text().replace(" ","_"))

        if len(pt_id) < 80:
            pt_id = pt_id + " " * (80 - len(pt_id))
        elif len(pt_id) > 80:
            self.throw_alert("The patient ID fields must be less than 80 characters. You have "
                    + str(len(pt_id)) + " characters. Please edit your fields and try again.")
            return

        if self.rec_info_date_x.isChecked():
            rec_info_date = "X"
        else:
            rec_info_date = self.startdateedit.date().toString("dd-MMM-yyyy").upper()

        if self.rec_info_fields[1].text() == "" or self.rec_info_fields[1].text() == " ":
            self.rec_info_fields[1].setText("X")
        if self.rec_info_fields[2].text() == "" or self.rec_info_fields[2].text() == " ":
            self.rec_info_fields[2].setText("X")
        if self.rec_info_fields[3].text() == "" or self.rec_info_fields[3].text() == " ":
            self.rec_info_fields[3].setText("X")
        rec_info = ("Startdate " + rec_info_date + " "
                    + self.rec_info_fields[1].text().replace(" ","_")
                    + " " + self.rec_info_fields[2].text().replace(" ","_") + " "
                    + self.rec_info_fields[3].text().replace(" ","_")
                    + " " + self.rec_info_fields[4].text().replace(" ","_"))
        if len(rec_info) < 80:
            rec_info = rec_info + " " * (80 - len(rec_info))
        elif len(rec_info) > 80:
            self.throw_alert("The recording information fields must be less than "
                + "80 characters. You have " + str(len(rec_info))
                + " characters. Please edit your fields and try again.")
            return

        self.data.pt_id = pt_id
        self.data.rec_info = rec_info
        self.data.start_date = start_date
        self.data.start_time = start_time
        self.parent.save_sig_to_edf()
        self.close_window()

    def close_window(self):
        """ Close the window """
        self.parent.anon_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed."""
        self.parent.anon_win_open = 0
        event.accept()

    def copy_original(self):
        """ Copy original values to modified fields.
        """
        if self.cbox_copyoriginal.isChecked():
            if self.cbox_setdefaults.isChecked():
                self.cbox_setdefaults.setChecked(0)
            self.pt_id_fields[0].setText(self.oldpt_id_fields[0].text())
            if self.radio_pt_id_f2.isChecked():
                self.radio_pt_id_f.setChecked(1)
            elif self.radio_pt_id_m2.isChecked():
                self.radio_pt_id_m.setChecked(1)
            else:
                self.radio_pt_id_x.setChecked(1)
            if self.radio_pt_id_date_x2.isChecked():
                self.radio_pt_id_date_x.setChecked(1)
            else:
                self.radio_pt_id_date.setChecked(1)
            self.dobedit.setDate(self.dob.date())
            self.pt_id_fields[3].setText(self.oldpt_id_fields[3].text())
            self.pt_id_fields[4].setText(self.oldpt_id_fields[4].text())

            if self.rec_info_date_x2.isChecked():
                self.rec_info_date_x.setChecked(1)
            else:
                self.rec_info_date.setChecked(1)
            self.startdateedit.setDate(self.startdate.date())
            self.rec_info_fields[1].setText(self.oldrec_info_fields[1].text())
            self.rec_info_fields[2].setText(self.oldrec_info_fields[2].text())
            self.rec_info_fields[3].setText(self.oldrec_info_fields[3].text())
            self.rec_info_fields[4].setText(self.oldrec_info_fields[4].text())

            self.datetimefield_inputs[0].setDate(self.olddatetimefield_inputs[0].date())
            self.datetimefield_inputs[1].setTime(self.olddatetimefield_inputs[1].time())

    def set_defaults(self):
        """ Set all edit fields to default values.
        """
        if self.cbox_setdefaults.isChecked():
            if self.cbox_copyoriginal.isChecked():
                self.cbox_copyoriginal.setChecked(0)
            self.pt_id_fields[0].setText("X")
            self.radio_pt_id_x.setChecked(1)
            self.radio_pt_id_date_x.setChecked(1)
            self.pt_id_fields[3].setText("X")
            self.pt_id_fields[4].setText("")

            self.rec_info_date_x.setChecked(1)
            self.rec_info_fields[1].setText("X")
            self.rec_info_fields[2].setText("X")
            self.rec_info_fields[3].setText("X")
            self.rec_info_fields[4].setText("")

            self.datetimefield_inputs[0].setDate(QDate(2001,1,1))
            self.datetimefield_inputs[1].setTime(QTime(1,1,1))

    def _valid_date(self,datetext):
        date = datetext.split("-")
        if len(date) != 3:
            return -1
        if len(date[2]) != 4:
            return -1
        if len(date[0]) != 2:
            return -1
        if self.MONTHS.index(date[1]) == -1:
            return -1
        return 0

    def throw_alert(self, msg, text = ""):
        """ Throws an alert to the user.
        """
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Information)
        alert.setText(msg)
        alert.setInformativeText(text)
        alert.setWindowTitle("Warning")
        alert.exec_()
        self.resize( self.sizeHint() )

class QHLine(QFrame):
    """ Class for a horizontal line widget """
    def __init__(self):
        """ Constructor """
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
