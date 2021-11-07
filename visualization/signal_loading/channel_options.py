""" Module for loading channels """
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QListWidget, QPushButton,
                                QCheckBox, QLabel, QGridLayout, QScrollArea,
                                QListWidgetItem, QAbstractItemView, QFileDialog,)

from matplotlib.backends.qt_compat import QtWidgets

import numpy as np
import pyedflib
from predictions.prediction_info import PredictionInfo
from signal_loading.channel_info import convert_txt_chn_names
from signal_loading.organize_channels import OrganizeChannels
from signal_loading.color_options import ColorOptions

class ChannelOptions(QWidget):
    """ Class for the channel loading window """
    def __init__(self,data,parent):
        """ Constructor for channel loading.
        """
        super().__init__()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.width = int(parent.width / 4)
        self.height = int(parent.height / 2.5)
        self.left = int(centerPoint.x() - self.width / 2)
        self.top = int(centerPoint.y() - self.height / 2)
        self.title = 'Select signals'
        # if loading new data make copies in case user cancels loading channels
        self.new_load = 0
        if data.edf_fn != parent.ci.edf_fn:
            self.pi = PredictionInfo()
            self.new_load = 1
        else:
            self.pi = parent.pi
        self.data = data
        self.parent = parent
        self.organize_win_open = 0
        self.setup_ui()

    def setup_ui(self):
        """ Sets up UI for channel window.
        """
        layout = QGridLayout()
        grid_lt = QGridLayout()
        grid_rt = QGridLayout()

        self.scroll = QScrollArea()
        self.scroll.setMinimumWidth(120)
        self.scroll.setMinimumHeight(200) # would be better if resizable
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.chn_qlist = QListWidget()
        self.chn_qlist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.scroll.setWidget(self.chn_qlist)

        self.populate_chn_list()
        self.data.converted_chn_names = []
        self.data.convert_chn_names()
        self.ar1020 = self.data.can_do_bip_ar(1,0)
        self.bip1020 = self.data.can_do_bip_ar(0,0)
        self.ar1010 = self.data.can_do_bip_ar(1,1)
        self.data.total_nchns = len(self.data.chns2labels)

        self.setWindowTitle(self.title)

        lbl_info = QLabel("Select channels to plot: ")
        grid_lt.addWidget(lbl_info,0,0)

        self.scroll_chn_cbox = QScrollArea()
        self.scroll_chn_cbox.hide()
        self.scroll_chn_cbox.setWidgetResizable(True)
        self.scroll_chn_cbox.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_chn_cbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if self.ar1020:
            self.cbox_ar = QCheckBox("Average reference (10-20)",self)
            self.cbox_ar.toggled.connect(self.ar_checked)
            grid_lt.addWidget(self.cbox_ar,1,0)

            self.cbox_bip = QCheckBox("Bipolar (10-20)",self)
            self.cbox_bip.toggled.connect(self.bip_checked)
            grid_lt.addWidget(self.cbox_bip,2,0)
        elif self.bip1020:
            self.cbox_bip = QCheckBox("Bipolar (10-20)",self)
            self.cbox_bip.toggled.connect(self.bip_checked)
            grid_lt.addWidget(self.cbox_bip,1,0)

        if self.ar1010:
            self.cbox_ar1010 = QCheckBox("Average reference (10-10)",self)
            self.cbox_ar1010.toggled.connect(self.ar_checked1010)
            grid_lt.addWidget(self.cbox_ar1010,3,0)

        self.chn_cbox_list = QWidget()
        self.scroll_chn_cbox.setWidget(self.chn_cbox_list)
        self.chn_cbox_layout = QVBoxLayout()
        self.chn_cbox_list.setLayout(self.chn_cbox_layout)
        self.cbox_list_items = []
        for k in self.data.labels_from_txt_file.keys():
            self.add_txt_file(k)
        self.uncheck_txt_files()

        grid_lt.addWidget(self.scroll_chn_cbox,5,0)

        self.btn_loadtxtfile = QPushButton("Load text file",self)
        self.btn_loadtxtfile.clicked.connect(self.load_txt_file)
        grid_lt.addWidget(self.btn_loadtxtfile,6,0)

        if len(self.data.txt_file_fn) > 0:
            if self.data.use_loaded_txt_file:
                self.cbox_txtfile.setChecked(1)
            self.btn_loadtxtfile.setVisible(0)
            self.btn_cleartxtfile.setVisible(1)
            self.cbox_txtfile.setVisible(1)
            self.cbox_txtfile.setText(self.data.txt_file_fn)

        lbl = QLabel("")
        grid_lt.addWidget(lbl, 7,0)

        btn_organize = QPushButton('Organize', self)
        btn_organize.clicked.connect(self.organize)
        grid_lt.addWidget(btn_organize,8,0)

        btn_colors = QPushButton('Change colors', self)
        btn_colors.clicked.connect(self.chg_colors)
        grid_lt.addWidget(btn_colors,9,0)

        btn_exit = QPushButton('Ok', self)
        btn_exit.clicked.connect(self.okay_pressed)
        grid_lt.addWidget(btn_exit,10,0)

        grid_rt.addWidget(self.scroll,0,1)

        layout.addLayout(grid_lt,0,0)
        layout.addLayout(grid_rt,0,1)
        self.setLayout(layout)

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(QSize(self.width, self.height))

        if (not self.parent.argv.montage_file is None) and self.parent.init == 0:
            self.load_txt_file(self.parent.argv.montage_file)
            self.okay_pressed()
        else:
            self.show()

    def populate_chn_list(self):
        """ Fills the list with all of the channels in the edf file.
            PREDICTION channels are ignored and saved into self.pi
        """
        chns = self.data.chns2labels
        lbls = self.data.labels2chns
        self.data.pred_chn_data = []
        edf_reader_obj = pyedflib.EdfReader(self.data.edf_fn)
        # if len(self.unprocessed_data) > 0: # reset predicted
        #    self.parent.predicted = 0
        if len(chns) == 0:
            self.parent.throw_alert("There are no named channels in the file.")
            self.close_window()
        else:
            self.chn_items = []
            for i in range(len(chns)):
                if chns[i].find("PREDICTIONS") == -1:
                    self.chn_items.append(QListWidgetItem(chns[i], self.chn_qlist))
                    self.chn_qlist.addItem(self.chn_items[i])
                # elif len(self.unprocessed_data) > 0:
                # load in the prediction channels if they exist
                # if they do, then the file was saved which
                # means that there are a reasonable amount of channels
                elif self.new_load:
                    # self.data.pred_chn_data.append(self.unprocessed_data[i])
                    self.data.pred_chn_data.append(edf_reader_obj.readSignal(i))
                    lbls.pop(chns[i])
                    chns.pop(i)

            # if len(self.unprocessed_data) > 0 and len(self.data.pred_chn_data) != 0:
            if self.new_load and len(self.data.pred_chn_data) != 0:
                self.data.pred_chn_data = np.array(self.data.pred_chn_data)
                self.data.pred_chn_data = self.data.pred_chn_data.T
                if self.data.pred_chn_data.shape[1] > 1:
                    self.pi.pred_by_chn = 1
                else:
                    self.data.pred_chn_data = np.squeeze(self.data.pred_chn_data)
                if len(self.data.pred_chn_data) > 0:
                    self.pi.preds = self.data.pred_chn_data
                    self.pi.preds_to_plot = self.data.pred_chn_data
                    self.pi.preds_loaded = 1
                    self.pi.plot_loaded_preds = 1
                    self.pi.preds_fn = "loaded from .edf file"
                    self.pi.pred_width = ((self.data.fs * self.parent.max_time_temp) /
                                                self.pi.preds.shape[0])
                    self.parent.predicted = 1

            # select the previously selected channels if they exist
            if len(self.data.list_of_chns) != 0 and not self.new_load:
                for k in range(len(self.data.list_of_chns)):
                    self.chn_items[self.data.list_of_chns[k]].setSelected(True)
            self.scroll.show()

    def ar_checked(self):
        """ Called when average reference is checked.
        """
        cbox = self.sender()
        chns = self.data.get_chns(self.data.labelsAR1020)
        if cbox.isChecked():
            self.uncheck_txt_files()
            self.cbox_bip.setChecked(0)
            if self.ar1010:
                self.cbox_ar1010.setChecked(0)
            #    self.cbox_bip1010.setChecked(0)
            #elif self.bip1010:
            #    self.cbox_bip1010.setChecked(0)
            # select all AR channels, deselect all others
            self._select_chns(chns, 0)
        else:
            self._select_chns(chns, 1)

    def bip_checked(self):
        """ Called when bipolar is checked.
        """
        cbox = self.sender()
        chns = self.data.get_chns(self.data.labelsBIP1020)
        if cbox.isChecked():
            if self.ar1010:
                self.cbox_ar1010.setChecked(0)
        #        self.cbox_bip1010.setChecked(0)
        #    elif self.bip1010:
        #        self.cbox_bip1010.setChecked(0)
        if self.ar1020:
            chns = self.data.get_chns(self.data.labelsAR1020)
            if cbox.isChecked():
                self.cbox_ar.setChecked(0)
                self.uncheck_txt_files()
                self._select_chns(chns, 0)
            else:
                self._select_chns(chns, 1)
        elif cbox.isChecked():
            self.uncheck_txt_files()
            # select all bipolar channels, deselect all others
            self._select_chns(chns, 0)
        else:
            self._select_chns(chns, 1)

    def ar_checked1010(self):
        """ Called when average reference 1010 is called.
        """
        cbox = self.sender()
        chns = self.data.get_chns(self.data.labelsAR1010)
        if cbox.isChecked():
            self.uncheck_txt_files()
            self.cbox_bip.setChecked(0)
            self.cbox_ar.setChecked(0)
            # self.cbox_bip1010.setChecked(0)
            # select all AR channels, deselect all others
            self._select_chns(chns, 0)
        else:
            self._select_chns(chns, 1)

    #def bip_checked1010(self):
    """ Called when bipolar 1010 is called.
    """
    """
        cbox = self.sender()
        chns = self.data.get_chns(self.data.labelsBIP1010)
        if self.ar1020:
            chns = self.data.get_chns(self.data.labelsAR1010)
            if cbox.isChecked():
                self.cbox_ar.setChecked(0)
                self.uncheck_txt_files()
                if self.ar1010:
                    self.cbox_ar1010.setChecked(0)
                self.cbox_bip.setChecked(0)
                self._select_chns(chns, 0)
            else:
                self._select_chns(chns, 1)
        elif cbox.isChecked():
            self.uncheck_txt_files()
            self.cbox_bip.setChecked(0)
            # select all bipolar channels, deselect all others
            self._select_chns(chns, 0)
        else:
            self._select_chns(chns, 1)
    """
    def uncheck_txt_files(self):
        """ Deselect all text files.
        """
        for child in self.chn_cbox_list.children():
            for grand_child in child.children():
                if isinstance(grand_child, QCheckBox):
                    grand_child.setChecked(0)

    def txt_file_checked(self):
        """ Called if a text file is selected.
        """
        c = self.sender()
        name = c.text()
        chns = self.data.get_chns(self.data.labels_from_txt_file[name])
        if c.isChecked():
            if self.ar1020:
                self.cbox_ar.setChecked(0)
                self.cbox_bip.setChecked(0)
                if self.ar1010:
                    self.cbox_ar1010.setChecked(0)
                #    self.cbox_bip1010.setChecked(0)
            if self.bip1020:
                self.cbox_bip.setChecked(0)
                #if self.bip1010:
                #    self.cbox_bip1010.setChecked(0)
            for child in self.chn_cbox_list.children():
                for ch in child.children():
                    if isinstance(ch, QCheckBox):
                        if ch.text() != name:
                            ch.setChecked(0)
            self._select_chns(chns, 0)
            self.data.use_loaded_txt_file = 1
        else:
            self._select_chns(chns, 1)
            self.data.use_loaded_txt_file = 0

    def _select_chns(self, chns, deselect_only):
        """ Selects given channels.

            Args:
                chns - the channels to select / deselect
                deselect_only - whether to only deselect given channels
        """
        if deselect_only:
            for k, val in enumerate(chns):
                if val:
                    self.chn_items[k].setSelected(0)
        else:
            for k, val in enumerate(chns):
                if val:
                    self.chn_items[k].setSelected(1)
                else:
                    self.chn_items[k].setSelected(0)

    def add_txt_file(self, name):
        """ Called to load in the new text file and add to the list.
        """
        # show the scroll area if it is hidden
        if self.scroll_chn_cbox.isHidden():
            self.scroll_chn_cbox.show()
        # add text file to the list
        main_wid = QWidget()
        wid = QGridLayout()
        wid_name = QCheckBox(name)
        wid_name.toggled.connect(self.txt_file_checked)
        wid_name.setChecked(1)
        wid.addWidget(wid_name,0,0)
        main_wid.setLayout(wid)
        self.chn_cbox_layout.addWidget(main_wid)

    def load_txt_file(self, name = ""):
        """ Called to load a text file.
        """
        if self.parent.argv.montage_file is None or self.parent.init:
            name = QFileDialog.getOpenFileName(self, 'Open file','.','Text files (*.txt)')
            name = name[0]
        if name is None or len(name) == 0:
            return

        short_name = name.split('/')[-1]
        if len(name.split('/')[-1]) > 15:
            short_name = name.split('/')[-1][0:15] + "..."
        if short_name in self.data.labels_from_txt_file.keys():
            self.parent.throw_alert("Each loaded text file must have a unique "
                + "name (first 14 characters). Please rename your file.")
            return
        if self._check_chns(name, short_name):
            self.add_txt_file(short_name)
        else:
            # throw error
            self.parent.throw_alert("The channels in this file do not match"
                + " those of the .edf file you have loaded. Please check your file.")

    def _check_chns(self, txt_fn, txt_fn_short):
        """ Function to check that this file has the appropriate channel names.
            Sets self.data.labels_from_txt_file if valid.

            Args:
                txt_fn: the file name to be loaded
                txt_fn_short: the name to be used in the dict
            Returns:
                1 for sucess, 0 for at least one of the channels was not found in
                the .edf file
        """
        try:
            text_file = open(txt_fn, "r")
        except:
            self.parent.throw_alert("The .txt file is invalid.")
        lines = text_file.readlines()
        l = 0
        while l < len(lines):
            loc = lines[l].find("\n")
            if loc != -1:
                lines[l] = lines[l][0:loc]
            if len(lines[l]) == 0:
                lines.pop(l)
            else:
                l += 1
        text_file.close()
        ret = 1
        for l in lines:
            if not l in self.data.converted_chn_names and not l in self.data.labels2chns:
                ret = 0
        if ret:
            self.data.labels_from_txt_file[txt_fn_short] = []
            for i in range(len(lines)):
                if not lines[len(lines) - 1 - i] in self.data.converted_chn_names:
                    lines[len(lines) - 1 - i] = convert_txt_chn_names(lines[len(lines) - 1 - i])
                self.data.labels_from_txt_file[txt_fn_short].append(lines[len(lines) - 1 - i])
        return ret

    def check_multi_chn_preds(self):
        """ Check if plotting predictions by channel. If so, check
            whether the number of channels match.

            Sets parent.predicted to 1 if correct, 0 if incorrect.
        """
        if self.parent.pi.pred_by_chn and self.parent.predicted:
            if self.parent.ci.nchns_to_plot != self.parent.pi.preds_to_plot.shape[1]:
                self.parent.predicted = 0

    def overwrite_temp_info(self):
        """ If temporary data was created in case the user cancels loading channels,
            it is now overwritten.

            Things to be overwritten:
                - parent.edf_info
                - parent.data
                - parent.fs
                - parent.max_time
                - parent.pi
                - parent.ci
                - parent.predicted
                - parent.count (set to 0 if new load)
        """
        self.parent.edf_info = self.parent.edf_info_temp
        self.parent.max_time = self.parent.max_time_temp
        self.parent.pi.write_data(self.pi)
        self.parent.ci.write_data(self.data)
        self.data = self.parent.ci
        self.parent.sei.fn = self.parent.fn_full_temp
        if self.new_load:
            self.parent.count = 0
            self.parent.lbl_fn.setText("Plotting: " + self.parent.fn_temp)

    def organize(self):
        """ Function to open the window to change signal order.
        """
        if not self.parent.organize_win_open:
            ret = self.check()
            if ret == 0:
                self.parent.organize_win_open = 1
                self.parent.chn_org = OrganizeChannels(self.data, self.parent)
                self.parent.chn_org.show()
                self.close_window()

    def chg_colors(self):
        """ Function to open the window to change signal color.
        """
        if not self.parent.color_win_open:
            ret = self.check()
            if ret == 0:
                self.parent.color_win_open = 1
                self.parent.color_ops = ColorOptions(self.data, self.parent, self)
                self.parent.color_ops.show()
                self.close_window()

    def check(self):
        """ Function to check the clicked channels and exit.

            Returns:
                -1 if there are no selected channels, 0 otherwise
        """
        selected_list_items = self.chn_qlist.selectedItems()
        idxs = []
        for k in range(len(self.chn_items)):
            if self.chn_items[k] in selected_list_items:
                idxs.append(self.data.labels2chns[self.data.chns2labels[k]])
        if len(idxs) > self.parent.max_channels:
            self.parent.throw_alert("You may select at most " +
                                    str(self.parent.max_channels) + " to plot. " +
                                    "You have selected " + str(len(idxs)) + ".")
            return -1
        if len(idxs) == 0:
            self.parent.throw_alert("Please select channels to plot.")
            return -1
        # Overwrite if needed, and prepare to plot
        if self.new_load:
            self.overwrite_temp_info()
            if self.parent.si.plot_spec:
                self.parent.si.plot_spec = 0
                self.parent.removeSpecPlot()
        plot_bip_from_ar = 0
        if (self.ar1020 and self.cbox_bip.isChecked()):# or
            #self.ar1010 and self.cbox_bip1010.isChecked()):
            plot_bip_from_ar = 1
        mont_type, txt_file_name = self._get_mont_type()
        self.data.prepare_to_plot(idxs, self.parent, mont_type, plot_bip_from_ar, txt_file_name)
        # check if multi-chn pred and number of chns match
        self.check_multi_chn_preds()
        return 0

    def _get_mont_type(self):
        """ Gets the type of montage from the cboxes.

            Returns:
                0 = ar 1020
                1 = bip 1020
                2 = ar 1010
                3 = ar 1010
                4 = text file
                5 = selected channels don't match selection
                txt_file_name, the name of the text file
        """
        mont_type = 5
        txt_file_name = ""
        if self.ar1020 and self.cbox_ar.isChecked():
            mont_type = 0
        elif (self.ar1020 or self.bip1020) and self.cbox_bip.isChecked():
            mont_type = 1
        elif self.ar1010 and self.cbox_ar1010.isChecked():
            mont_type = 2
        #elif self.bip1010 and self.cbox_bip1010.isChecked():
        #    mont_type = 3
        else:
            for child in self.chn_cbox_list.children():
                for ch in child.children():
                    if isinstance(ch, QCheckBox) and ch.isChecked():
                        txt_file_name = ch.text()
                        mont_type = 4
        return mont_type, txt_file_name

    def okay_pressed(self):
        """ Called when okay is pressed. Calls check function and returns
            if channels were sucessfully selected.
        """
        ret = self.check()
        if ret == 0:
            self.parent.call_initial_move_plot()
            self.close_window()

    def close_window(self):
        """ Closes the window.
        """
        self.parent.chn_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.chn_win_open = 0
        event.accept()
