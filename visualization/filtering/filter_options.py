""" Module for filtering options window. """
from PyQt5.QtWidgets import (QWidget, QPushButton, QCheckBox, QLabel,
                                QGridLayout, QDoubleSpinBox)

from matplotlib.backends.qt_compat import QtWidgets


class FilterOptions(QWidget):
    """ Class for filtering options window. """
    def __init__(self,data,parent):
        """ Constructor.

            Args:
                data - the filter_info object
                parent - the main (parent) window
        """
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Filter Options'
        self.width = parent.width / 5
        self.height = parent.height / 3
        self.data = data
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """ Setup the UI for the filter options window.
        """
        layout = QGridLayout()
        self.setWindowTitle(self.title)
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.setGeometry(center_point.x() - self.width / 2,
                center_point.y() - self.height / 2, self.width, self.height)

        self.btn_exit = QPushButton('Ok', self)
        layout.addWidget(self.btn_exit,4,3)

        self.cbox_lp = QCheckBox("Lowpass",self)
        self.cbox_lp.setToolTip("Click to filter")
        if self.data.do_lp:
            self.cbox_lp.setChecked(True)
        layout.addWidget(self.cbox_lp,0,0)

        self.btn_get_lp = QDoubleSpinBox(self)
        self.btn_get_lp.setValue(self.data.lp)
        self.btn_get_lp.setRange(0, self.data.fs / 2)
        layout.addWidget(self.btn_get_lp,0,1)

        lp_hz_lbl = QLabel("Hz",self)
        layout.addWidget(lp_hz_lbl,0,2)

        self.cbox_hp= QCheckBox("Highpass",self)
        self.cbox_hp.setToolTip("Click to filter")
        if self.data.do_hp:
            self.cbox_hp.setChecked(True)
        layout.addWidget(self.cbox_hp,1,0)

        self.btn_get_hp = QDoubleSpinBox(self)
        self.btn_get_hp.setValue(self.data.hp)
        self.btn_get_hp.setRange(0, self.data.fs / 2)
        layout.addWidget(self.btn_get_hp,1,1)

        hp_hz_lbl = QLabel("Hz",self)
        layout.addWidget(hp_hz_lbl,1,2)

        self.cbox_notch = QCheckBox("Notch",self)
        self.cbox_notch.setToolTip("Click to filter")
        if self.data.do_notch:
            self.cbox_notch.setChecked(True)
        layout.addWidget(self.cbox_notch,2,0)

        self.btn_get_notch = QDoubleSpinBox(self)
        self.btn_get_notch.setValue(self.data.notch)
        self.btn_get_notch.setRange(0, self.data.fs / 2)
        layout.addWidget(self.btn_get_notch,2,1)

        notch_hz_lbl = QLabel("Hz",self)
        layout.addWidget(notch_hz_lbl,2,2)

        self.cbox_bp = QCheckBox("Bandpass",self)
        self.cbox_bp.setToolTip("Click to filter")
        if self.data.do_bp:
            self.cbox_bp.setChecked(True)
        layout.addWidget(self.cbox_bp,3,0)

        self.btn_get_bp1 = QDoubleSpinBox(self)
        self.btn_get_bp1.setValue(self.data.bp1)
        self.btn_get_bp1.setRange(0, self.data.fs / 2)
        layout.addWidget(self.btn_get_bp1,3,1)

        bp_to_lbl = QLabel("to",self)
        layout.addWidget(bp_to_lbl,3,2)

        self.btn_get_bp2 = QDoubleSpinBox(self)
        self.btn_get_bp2.setValue(self.data.bp2)
        self.btn_get_bp2.setRange(0, self.data.fs / 2)
        layout.addWidget(self.btn_get_bp2,3,3)

        notch_hz_lbl = QLabel("Hz",self)
        layout.addWidget(notch_hz_lbl,3,4)

        self.setLayout(layout)
        self.set_signals_slots()
        self.show()

    def set_signals_slots(self):
        """ Setup signals and slots.
        """
        self.btn_exit.clicked.connect(self.change)
        self.cbox_lp.toggled.connect(self.lp_filter_checked)
        self.cbox_hp.toggled.connect(self.hp_filter_checked)
        self.cbox_notch.toggled.connect(self.notch_filter_checked)
        self.cbox_bp.toggled.connect(self.bp_filter_checked)

    def lp_filter_checked(self):
        """ Called when the lp filter cbox is toggled.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.data.do_lp = 1
            self.cbox_bp.setChecked(0)
        else:
            self.data.do_lp = 0

    def hp_filter_checked(self):
        """ Called when the hp filter cbox is toggled.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.data.do_hp = 1
            self.cbox_bp.setChecked(0)
        else:
            self.data.do_hp = 0

    def notch_filter_checked(self):
        """ Called when the notch filter cbox is toggled.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.data.do_notch = 1
        else:
            self.data.do_notch = 0

    def bp_filter_checked(self):
        """ Called when the bandpass filter cbox is checked.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.data.do_bp = 1
            self.cbox_lp.setChecked(0)
            self.cbox_hp.setChecked(0)
        else:
            self.data.do_bp = 0

    def change(self):
        """ Checks to make sure values are legal and updates
            the FilterInfo object
        """
        hp = self.btn_get_hp.value()
        lp = self.btn_get_lp.value()
        bp1 = self.btn_get_bp1.value()
        bp2 = self.btn_get_bp2.value()
        if ((0 < lp < self.data.fs / 2) and
            (0 < hp < self.data.fs / 2)):
            if lp - hp > 0:
                if self.data.do_lp:
                    self.data.lp = self.btn_get_lp.value()
                if self.data.do_hp:
                    self.data.hp = self.btn_get_hp.value()
        if 0 < bp1 < bp2:
            if self.data.do_bp:
                self.data.bp1 = bp1
                self.data.bp2 = bp2
        else:
            self.data.do_bp = 0
        if self.btn_get_notch.value() > 0 and self.btn_get_notch.value() < self.data.fs / 2:
            if self.data.do_notch:
                self.data.notch = self.btn_get_notch.value()
        else:
            self.data.do_notch = 0
        self.parent.call_move_plot(0,0,0)
        self.close_window()

    def close_window(self):
        """ Closes the window.
        """
        self.parent.filter_win_open = 0
        self.close()
