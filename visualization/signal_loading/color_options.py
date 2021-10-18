""" Module for the color options class """
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QListWidget, QPushButton, QLabel,
                                QGridLayout, QScrollArea, QListWidgetItem,
                                QAbstractItemView, QGroupBox, QRadioButton,
                                QHBoxLayout, QColorDialog)

from signal_loading.channel_info import ChannelInfo

from matplotlib.backends.qt_compat import QtWidgets


class ColorOptions(QWidget):
    """ Class for the color options channel """
    def __init__(self,data,parent,chn_ops):
        """ Constructor for color options.

            Args:
                data - the channel info object
                parent - the main (parent) window
                chn_ops - the channel options window
        """
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Choose colors'
        self.width = parent.width / 6
        self.height = parent.height / 3
        self.data = data
        self.parent = parent
        self.chn_ops = chn_ops
        self.lt_custom = "#ffffff"
        self.rt_custom = "#ffffff"
        self.mid_custom = "#ffffff"
        self.setup_ui()

    def setup_ui(self):
        """ Setup UI for the color options window.
        """
        self.setWindowTitle(self.title)
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.setGeometry(centerPoint.x() - self.width / 2,
                centerPoint.y() - self.height / 2, self.width, self.height)
        
        grid_lt = QGridLayout()
        
        lbl_info = QLabel("Select the color for each channel:\nPlease note that any non-standard channel "
                        + "\nor names not recognized by the program will be "
                        + "\nassigned the color of the midline.")
        grid_lt.addWidget(lbl_info,0,0)

        lbl_left = QLabel("Left hemisphere:")
        grid_lt.addWidget(lbl_left,1,0)
        lbl_right = QLabel("Right hemisphere:")
        grid_lt.addWidget(lbl_right,2,0)
        lbl_mid = QLabel("Midline:")
        grid_lt.addWidget(lbl_mid,3,0)

        groupbox_left_colors = QGroupBox()
        self.radio_col_r_lt = QRadioButton("R")
        self.radio_col_g_lt = QRadioButton("G")
        self.radio_col_b_lt = QRadioButton("B")
        self.radio_col_k_lt = QRadioButton("")
        self.k_btn_lt = QPushButton("Custom")
        self.k_btn_lt.clicked.connect(self.select_col_k_lt)
        hbox_left = QHBoxLayout()
        hbox_left.addWidget(self.radio_col_r_lt)
        hbox_left.addWidget(self.radio_col_g_lt)
        hbox_left.addWidget(self.radio_col_b_lt)
        hbox_left.addWidget(self.radio_col_k_lt)
        hbox_left.addWidget(self.k_btn_lt)
        groupbox_left_colors.setLayout(hbox_left)
        grid_lt.addWidget(groupbox_left_colors, 1,1)

        groupbox_right_colors = QGroupBox()
        self.radio_col_r_rt = QRadioButton("R")
        self.radio_col_g_rt = QRadioButton("G")
        self.radio_col_b_rt = QRadioButton("B")
        self.radio_col_k_rt = QRadioButton("")
        self.k_btn_rt = QPushButton("Custom")
        self.k_btn_rt.clicked.connect(self.select_col_k_rt)
        hbox_right = QHBoxLayout()
        hbox_right.addWidget(self.radio_col_r_rt)
        hbox_right.addWidget(self.radio_col_g_rt)
        hbox_right.addWidget(self.radio_col_b_rt)
        hbox_right.addWidget(self.radio_col_k_rt)
        hbox_right.addWidget(self.k_btn_rt)
        groupbox_right_colors.setLayout(hbox_right)
        grid_lt.addWidget(groupbox_right_colors, 2,1)

        groupbox_mid_colors = QGroupBox()
        self.radio_col_r_mid = QRadioButton("R")
        self.radio_col_g_mid = QRadioButton("G")
        self.radio_col_b_mid = QRadioButton("B")
        self.radio_col_k_mid = QRadioButton("")
        self.k_btn_mid = QPushButton("Custom")
        self.k_btn_mid.clicked.connect(self.select_col_k_mid)
        hbox_mid = QHBoxLayout()
        hbox_mid.addWidget(self.radio_col_r_mid)
        hbox_mid.addWidget(self.radio_col_g_mid)
        hbox_mid.addWidget(self.radio_col_b_mid)
        hbox_mid.addWidget(self.radio_col_k_mid)
        hbox_mid.addWidget(self.k_btn_mid)
        groupbox_mid_colors.setLayout(hbox_mid)
        grid_lt.addWidget(groupbox_mid_colors, 3,1)

        self._set_init_col("lt")
        self._set_init_col("rt")
        self._set_init_col("mid")

        btn_exit = QPushButton('Ok', self)
        btn_exit.clicked.connect(self.check)
        grid_lt.addWidget(btn_exit,4,0)
        self.setLayout(grid_lt)

        self.show()

    def select_col_k_lt(self):
        """ Color picker.
        """
        color = QColorDialog.getColor()
        self.sender().setStyleSheet("background-color: " + color.name())
        self.lt_custom = color.name()

    def select_col_k_rt(self):
        """ Color picker.
        """
        color = QColorDialog.getColor()
        self.sender().setStyleSheet("background-color: " + color.name())
        self.rt_custom = color.name()

    def select_col_k_mid(self):
        """ Color picker.
        """
        color = QColorDialog.getColor()
        self.sender().setStyleSheet("background-color: " + color.name())
        self.mid_custom = color.name()

    def _set_init_col(self, hemi):
        """ Function to set the initial color.

            Args:
                hemi: "lt", "rt", or "mid"
        """
        if eval("self.data." + hemi + "_col") == "r":
            eval("self.radio_col_r_" + hemi).setChecked(1)
        elif eval("self.data." + hemi + "_col") == "b":
            eval("self.radio_col_b_" + hemi).setChecked(1)
        elif eval("self.data." + hemi + "_col") == "#1f8c45":
            eval("self.radio_col_g_" + hemi).setChecked(1)
        else:
            eval("self.radio_col_k_" + hemi).setChecked(1)
            eval("self.k_btn_" + hemi).setStyleSheet(
                "background-color: " + eval("self.data." + hemi + "_col"))

    def _get_col(self, hemi):
        """ Function to get the color.

            Args:
                hemi: "lt", "rt", or "mid"
            Returns:
                the color in hex
        """
        if eval("self.radio_col_r_" + hemi).isChecked():
            return "r"
        elif eval("self.radio_col_b_" + hemi).isChecked():
            return "b"
        elif eval("self.radio_col_g_" + hemi).isChecked():
            return '#1f8c45'
        else:
            col = eval("self." + hemi + "_custom")
            if col == "#ffffff":
                self.parent.throw_alert("Please click \"Custom\" to select a custom color.")
                return ""
            return col

    def check(self):
        """ Function to get colors and exit.
        """
        if (self._get_col("rt") == "" or self._get_col("lt") == ""
            or self._get_col("mid") == ""):
            return
        self.data.rt_col = self._get_col("rt")
        self.data.lt_col = self._get_col("lt")
        self.data.mid_col = self._get_col("mid")
        # redo setting data, channel names, and colors
        self.chn_ops.check()
        self.parent.call_initial_move_plot()
        self.close_window()

    def close_window(self):
        """ Closes the window.
        """
        self.parent.color_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.color_win_open = 0
        event.accept()
