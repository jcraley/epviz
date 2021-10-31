""" Module for spectrogram options window """
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QGridLayout,
                                QComboBox, QDoubleSpinBox, QDesktopWidget)
from PyQt5.QtGui import QFont
from matplotlib.backends.qt_compat import QtWidgets

from visualization.plot_utils import filter_data
import numpy as np
from scipy import signal

class SpecOptions(QWidget):
    """ Class for spectrogram options window """
    def __init__(self, data, parent):
        """ Constructor """
        super().__init__()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.width = int(parent.width / 3)
        self.height = int(parent.height / 2.5)
        self.left = int(centerPoint.x() - self.width / 2)
        self.top = int(centerPoint.y() - self.height / 2)
        self.title = 'Select signal for spectrogram'
        self.data = data
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """ Setup the UI """
        self.setWindowTitle(self.title)

        grid = QGridLayout()

        self.chn_combobox = QComboBox()
        self.chn_combobox.addItems(["<select channel>"])

        lbl_info = QLabel("To hide the plot, click \n\"Clear\" and then \"Ok\".")
        grid.addWidget(lbl_info, 3, 0)
        my_font=QFont()
        my_font.setBold(True)
        lbl_info.setFont(my_font)

        lbl_chn = QLabel("Select a channel for \nspectrogram plotting: ")
        grid.addWidget(lbl_chn, 1, 0)
        grid.addWidget(self.chn_combobox, 1, 1, 1, 3)

        lblfsaxis = QLabel("x-axis (Hz): ")
        grid.addWidget(lblfsaxis, 2, 0)
        self.btn_get_min_fs = QDoubleSpinBox(self)
        self.btn_get_min_fs.setRange(0, self.parent.edf_info.fs / 2)
        self.btn_get_min_fs.setValue(self.data.min_fs)
        self.btn_get_min_fs.setDecimals(3)
        grid.addWidget(self.btn_get_min_fs, 2, 1)
        lblfsto = QLabel(" to ")
        grid.addWidget(lblfsto, 2, 2)
        self.btn_get_max_fs = QDoubleSpinBox(self)
        self.btn_get_max_fs.setDecimals(3)
        self.btn_get_max_fs.setRange(0, self.parent.edf_info.fs / 2)
        self.btn_get_max_fs.setValue(self.data.max_fs)
        grid.addWidget(self.btn_get_max_fs, 2, 3)

        self.btn_clear = QPushButton('Clear', self)
        grid.addWidget(self.btn_clear, 3, 1, 1, 2)
        self.btn_exit = QPushButton('Ok', self)
        grid.addWidget(self.btn_exit, 3, 3)

        self.setLayout(grid)

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(QSize(self.width, self.height))

        self.set_sig_slots()

    def set_sig_slots(self):
        """ Set signals and slots """
        self.populate_chn_list()
        self.btn_exit.clicked.connect(self.check)
        self.btn_clear.clicked.connect(self.clear_spec)

        self.show()

    def populate_chn_list(self):
        """ Fills the list with all of the channels to be loaded.
        """
        self.chn_items = []
        self.labels_flipped = []
        labels_to_plot = self.parent.ci.labels_to_plot
        if len(labels_to_plot) == 0:
            self.close_window()
        else:
            for i in range(len(labels_to_plot) - 1):
                self.labels_flipped.append(labels_to_plot[i + 1])
                self.chn_combobox.addItems([labels_to_plot[len(labels_to_plot) - 1 - i]])
            if self.data.chn_plotted != -1:
                self.chn_combobox.setCurrentIndex(len(labels_to_plot) - self.data.chn_plotted - 1)
            else:
                self.chn_combobox.setCurrentIndex(0)

    def clear_spec(self):
        """ Function to clear the current channel
        """
        self.chn_combobox.setCurrentIndex(0)
        self.data.chn_plotted = -1

    def check(self):
        """ Function to check the clicked channel and exit.
        """
        row = self.chn_combobox.currentIndex()
        if row != 0:
            nchns = self.parent.ci.nchns_to_plot
            self.data.chn_plotted = nchns - row
            self.data.chn_name = self.labels_flipped[len(self.labels_flipped) - row]
            self.data.data = self.parent.ci.data_to_plot[self.data.chn_plotted,:]
            fs = self.parent.edf_info.fs
            if self.parent.filter_checked == 1:
                self.data.data = np.squeeze(filter_data(np.array(self.data.data)[np.newaxis,:], fs, self.parent.fi))
            if not self.data.plot_spec:
                self.data.plot_spec = 1
                self.parent.make_spec_plot()
            else:
                self.parent.update_spec_chn()
        elif self.data.plot_spec:
            self.data.plot_spec = 0
            self.parent.remove_spec_plot()
            self.data.chn_plotted = -1
        if self.btn_get_max_fs.value() > self.btn_get_min_fs.value():
            self.data.max_fs = self.btn_get_max_fs.value()
            self.data.min_fs = self.btn_get_min_fs.value()
            self.close_window()
        elif self.data.plot_spec:
            self.parent.throw_alert("Maximum frequency must be greater than minimum frequency.")
        else:
            self.close_window()

    def close_window(self):
        """ Called to close the window and exit
        """
        self.parent.spec_win_open = 0
        self.parent.call_move_plot(0,0)
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.spec_win_open = 0
        event.accept()
