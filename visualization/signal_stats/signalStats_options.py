""" Module to hold the stats fs band options class """
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QWidget, QListWidget, QPushButton, QLabel,
                                QGridLayout, QScrollArea, QListWidgetItem,
                                QAbstractItemView, QGroupBox, QRadioButton,
                                QHBoxLayout, QColorDialog, QLineEdit,
                                QDoubleSpinBox, QDesktopWidget)

from signal_loading.channel_info import ChannelInfo

from matplotlib.backends.qt_compat import QtWidgets

class SignalStatsOptions(QWidget):
    """ Class for the stat fs band options channel """
    def __init__(self, data, parent):
        """ Constructor for stat fs band options.

            Args:
                data - the signalStats_info object
                parent - the main (parent) window
        """
        super().__init__()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.title = 'Add frequency band'
        self.width = int(parent.width / 6)
        self.height = int(parent.height / 4)
        self.left = int(centerPoint.x() - self.width / 2)
        self.top = int(centerPoint.y() - self.height / 2)
        self.data = data
        self.parent = parent
        self.fs_band_count = len(self.data.fs_bands.keys()) - 5
        self.fs_band_lbls = {}
        self.setup_ui()

    def setup_ui(self):
        """ Setup UI for the color options window.
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(QSize(self.width, self.height))
        
        grid_lt = QGridLayout()
        
        lbl_info = QLabel("Add a frequency band with a name. You may add up to 5.")
        grid_lt.addWidget(lbl_info, 0, 0, 1, 5)

        lbl_name = QLabel("Name: ")
        grid_lt.addWidget(lbl_name, 1, 0)
        self.input_name = QLineEdit()
        grid_lt.addWidget(self.input_name, 1, 1)
        lbl_fs = QLabel("Frequency: ")
        grid_lt.addWidget(lbl_fs, 1, 2)
        self.input_fs0 = QDoubleSpinBox(self)
        self.input_fs0.setValue(0)
        self.input_fs0.setRange(0, self.parent.edf_info.fs / 2)
        grid_lt.addWidget(self.input_fs0, 1, 3)
        lbl_fs_to = QLabel(" to ")
        grid_lt.addWidget(lbl_fs_to, 1, 4)
        self.input_fs1 = QDoubleSpinBox(self)
        self.input_fs1.setValue(0)
        self.input_fs1.setRange(0, self.parent.edf_info.fs / 2)
        grid_lt.addWidget(self.input_fs1, 1, 5)
        hz_lbl = QLabel("Hz")
        grid_lt.addWidget(hz_lbl, 1, 6)
        self.btn_add = QPushButton("+")
        grid_lt.addWidget(self.btn_add, 1,7)

        self.grid_list = QGridLayout()
        grid_lt.addLayout(self.grid_list, 2, 0, 1, 7)
        
        prev_fs = ["alpha", "beta", "gamma", "delta", "theta"]
        for fs_band in self.data.fs_bands.keys():
            if not fs_band in prev_fs:
                self.fs_band_lbls[fs_band] = QLabel(
                    fs_band + ": " + str(self.data.fs_bands[fs_band][0]) + " to "
                    + str(self.data.fs_bands[fs_band][1]) + "Hz")
                self.grid_list.addWidget(self.fs_band_lbls[fs_band])

        self.btn_exit = QPushButton('Ok', self)
        grid_lt.addWidget(self.btn_exit,3,5, 1, 2)
        self.setLayout(grid_lt)

        self.set_signals_slots()

        self.show()

    def set_signals_slots(self):
        """ Set signals and slots.
        """
        self.btn_add.clicked.connect(self.add_fs_band)
        self.btn_exit.clicked.connect(self.check)

    def add_fs_band(self):
        """ Add a new fs band.
        """
        if self.fs_band_count < 5:
            if self._check_valid():
                # if valid, create new labels below
                self.fs_band_lbls[self.input_name.text()] = QLabel(
                    self.input_name.text() + ": " + str(self.input_fs0.value()) + " to "
                    + str(self.input_fs1.value()) + "Hz")
                self.grid_list.addWidget(self.fs_band_lbls[self.input_name.text()])
                # add to fs_bands
                self.data.fs_bands[self.input_name.text()] = (self.input_fs0.value(),
                                                              self.input_fs1.value())
                # reset fields
                self.input_name.setText("")
                self.input_fs0.setValue(0)
                self.input_fs1.setValue(0)
                self.fs_band_count += 1
        else:
            self.parent.throw_alert("You have up to 5 additional frequency ranges.")

    def _check_valid(self):
        """ Check that the current input is valid. 

            Returns:
                1 for sucess, 0 for failure
        """
        if len(self.input_name.text()) == 0:
            self.parent.throw_alert("You must enter a name in order to add a frequency band.")
            return 0
        if len(self.input_name.text()) > 10:
            self.parent.throw_alert("Name must be 10 characters or less.")
            return 0
        if self.input_name.text() in self.data.fs_bands.keys():
            self.parent.throw_alert("This name is already in use. The name must be unique.")
            return 0
        if self.input_fs0.value() >= self.input_fs1.value():
            self.parent.throw_alert("The first frequency must be less than the second frequency.")
            return 0
        return 1

    def check(self):
        """ Function to get colors and exit.
        """
        # add all new bands as labels
        ud = 5 + len(self.data.fs_bands.keys())
        curr = 0
        for fs_band in self.data.fs_bands.keys():
            if not fs_band in self.parent.fs_band_lbls.keys():
                lbl = QtWidgets.QLabel()
                lbl.setText(fs_band + ":")
                self.parent.grid_layout.addWidget(lbl, ud + curr, 1, 1, 1)
                self.parent.fs_band_lbls[fs_band] = QtWidgets.QLabel()
                self.parent.fs_band_lbls[fs_band].setText("")
                self.parent.grid_layout.addWidget(self.parent.fs_band_lbls[fs_band], ud + curr, 2, 1, 1)
                self.parent.fs_band_sel_lbls[fs_band] = QtWidgets.QLabel()
                self.parent.fs_band_sel_lbls[fs_band].setText("")
                self.parent.grid_layout.addWidget(self.parent.fs_band_sel_lbls[fs_band], ud + curr, 3, 1, 1)
                curr += 1
        # update the fields on the side panel
        self.parent.stat_time_select_changed()
        self.parent.set_fs_band_lbls()
        self.close_window()

    def close_window(self):
        """ Closes the window.
        """
        self.parent.stat_fs_band_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.stat_fs_band_win_open = 0
        event.accept()
