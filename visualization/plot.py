""" Module for main plotting window """
import argparse as ap
from os import path
import sys

from signal_loading.channel_info import ChannelInfo
from signal_loading.channel_options import ChannelOptions
from filtering.filter_options import FilterOptions
from filtering.filter_info import FilterInfo
from predictions.pred_options import PredictionOptions
from predictions.preds_info import PredsInfo
from spectrogram_window.spec_options import SpecOptions
from spectrogram_window.spec_info import SpecInfo
from image_saving.saveImg_info import SaveImgInfo
from image_saving.saveImg_options import SaveImgOptions
from image_saving.saveTopoplot_options import SaveTopoplotOptions
from edf_saving.saveEdf_info import SaveEdfInfo
from edf_saving.saveEdf_options import SaveEdfOptions
from signal_stats.signalStats_info import SignalStatsInfo
from signal_stats.signalStats_options import SignalStatsOptions

import pyedflib
from plot_utils import check_annotations, filter_data, convert_from_count, get_time
from montages import *
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.qt_compat import QtCore, QtWidgets
import matplotlib
matplotlib.use("Qt5Agg")
import mne

from PyQt5.QtCore import Qt, QTime, QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog,
                             QMessageBox, QWidget,
                             QPushButton, QCheckBox, QLabel, QInputDialog,
                             QSlider, QGridLayout, QDockWidget, QListWidget,
                             QListWidgetItem, QLineEdit, QSpinBox,
                             QTimeEdit, QComboBox, QFrame, QStyle)
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QDesktopServices
import pyqtgraph as pg
from pyqtgraph.dockarea import *

from preprocessing.edf_loader import *
from scipy import signal

class MainPage(QMainWindow):
    """ Class for main plottintg window """

    def __init__(self, argv, app):
        """ Main window constructor

            Args:
                argv - the command line arguments
                app - the pyqt app instance
        """
        super().__init__()
        self.argv = argv
        self.left = 10
        self.top = 10
        self.title = 'EEG Prediction Visualization (EPViz)'
        size_object = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width = int(size_object.width() * 0.9)
        self.height = int(size_object.height() * 0.7)
        self.app = app
        self.init_ui()

    def init_ui(self):
        """ Setup the UI
        """
        style_file = open('visualization/ui_files/gui_stylesheet.css')
        self.app.setStyleSheet(style_file.read())
        style_file.close()
        layout = QGridLayout()
        layout.setSpacing(10)
        grid_lt = QGridLayout()
        self.grid_rt = QGridLayout()

        #---- left side of the screen ----#

        ud = 0

        self.button_select_file = QPushButton('Select file', self)
        self.button_select_file.setToolTip('Click to select EDF file')
        grid_lt.addWidget(self.button_select_file, ud, 0, 1, 2)
        ud += 1

        self.lbl_fn = QLabel("No file loaded.",self)
        grid_lt.addWidget(self.lbl_fn, ud, 0, 1, 2)
        ud += 1

        self.button_chg_sig = QPushButton("Change signals", self)
        self.button_chg_sig.setToolTip("Click to change signals")
        grid_lt.addWidget(self.button_chg_sig, ud, 1)
        ud += 1

        self.cbox_filter = QCheckBox("Filter signals", self)
        self.cbox_filter.setToolTip("Click to filter")
        grid_lt.addWidget(self.cbox_filter, ud, 0)

        self.button_chg_filt = QPushButton("Change Filter", self)
        self.button_chg_filt.setToolTip("Click to change filter")
        grid_lt.addWidget(self.button_chg_filt, ud, 1)
        ud += 1

        test01 = QLabel("", self)
        grid_lt.addWidget(test01, ud, 0)
        ud += 1

        grid_lt.addWidget(QHLine(), ud, 0, 1, 2)
        ud += 1

        test0 = QLabel("", self)
        grid_lt.addWidget(test0, ud, 0)
        ud += 1

        self.button_predict = QPushButton("Load model / predictions", self)
        self.button_predict.setToolTip("Click load data, models, and predictions")
        grid_lt.addWidget(self.button_predict, ud, 0, 1, 2)
        ud += 1

        self.pred_label = QLabel("", self)
        grid_lt.addWidget(self.pred_label, ud, 0, 1, 1)
        ud += 1

        self.thresh_lbl = QLabel("Change threshold of prediction:  (threshold = 0.5)", self)
        grid_lt.addWidget(self.thresh_lbl, ud, 0,1,2)
        ud += 1

        self.thresh_slider = QSlider(Qt.Horizontal, self)
        self.thresh_slider.setMinimum(0)
        self.thresh_slider.setMaximum(100)
        self.thresh_slider.setValue(50)
        grid_lt.addWidget(self.thresh_slider, ud, 0, 1, 2)
        ud += 1

        self.btn_topo = QPushButton("Show topoplots", self)
        self.btn_topo.setToolTip("Click to show topoplot. Only enabled" +
                                " if muli-channel predictions are plotted.")
        self.btn_topo.setEnabled(0)
        grid_lt.addWidget(self.btn_topo, ud, 1, 1, 1)
        ud += 1

        test = QLabel("", self)
        grid_lt.addWidget(test, ud, 0)
        ud += 1

        grid_lt.addWidget(QHLine(), ud, 0, 1, 2)
        ud += 1

        test11 = QLabel("", self)
        grid_lt.addWidget(test11, ud, 0)
        ud += 1

        self.btn_zoom = QPushButton("Open zoom", self)
        self.btn_zoom.setToolTip("Click to open the zoom window")
        grid_lt.addWidget(self.btn_zoom, ud, 0)

        self.button_chg_spec = QPushButton("Power spectrum", self)
        self.button_chg_spec.setToolTip("Click to plot the spectrogram of a signal")
        grid_lt.addWidget(self.button_chg_spec, ud, 1)
        ud += 1

        label_view_ops = QLabel("View options:", self)
        label_view_ops.setAlignment(Qt.AlignCenter)
        grid_lt.addWidget(label_view_ops, ud, 0, 1, 2)
        ud += 1

        label_amp = QLabel("Change amplitude:", self)
        grid_lt.addWidget(label_amp, ud, 0)

        self.button_amp_inc = QPushButton("+", self)
        self.button_amp_inc.setToolTip("Click to increase signal amplitude")
        grid_lt.addWidget(self.button_amp_inc, ud, 1)
        ud += 1

        self.button_amp_dec = QPushButton("-", self)
        self.button_amp_dec.setToolTip("Click to decrease signal amplitude")
        grid_lt.addWidget(self.button_amp_dec, ud, 1)
        ud += 1

        label_ws = QLabel("Window size:", self)
        grid_lt.addWidget(label_ws, ud, 0)

        self.ws_combobox = QComboBox()
        self.ws_combobox.addItems(["1s","5s","10s","15s","20s","25s","30s"])
        self.ws_combobox.setCurrentIndex(2)
        grid_lt.addWidget(self.ws_combobox, ud, 1)
        ud += 1


        test2 = QLabel("", self)
        grid_lt.addWidget(test2, ud, 0)
        ud += 1

        grid_lt.addWidget(QHLine(), ud, 0, 1, 2)
        ud += 1

        test11 = QLabel("", self)
        grid_lt.addWidget(test11, ud, 0)
        ud += 1

        self.button_print = QPushButton("Export to .png", self)
        self.button_print.setToolTip("Click to print a copy of the graph")
        grid_lt.addWidget(self.button_print, ud, 0)

        self.button_save_edf = QPushButton("Save to .edf", self)
        self.button_save_edf.setToolTip("Click to save current signals to an .edf file")
        grid_lt.addWidget(self.button_save_edf, ud, 1)
        ud += 1

        test3 = QLabel("", self)
        grid_lt.addWidget(test3, ud, 0)
        ud += 1
        test4 = QLabel("", self)
        grid_lt.addWidget(test4, ud, 0)
        ud += 1
        test5 = QLabel("", self)
        grid_lt.addWidget(test5, ud, 0)
        ud += 1
        test6 = QLabel("", self)
        grid_lt.addWidget(test6, ud, 0)
        ud += 1

        self.btn_help = QPushButton('Help')
        self.btn_help.setIcon(self.style().standardIcon(
                    getattr(QStyle, 'SP_TitleBarContextHelpButton')))
        grid_lt.addWidget(self.btn_help,ud,0)

        #---- end left side ----#


        #---- Right side of the screen ----#
        self.plot_layout = pg.GraphicsLayoutWidget()
        self.main_plot = self.plot_layout.addPlot(row=0, col=0)
        self.main_plot.setMouseEnabled(x=False, y=False)
        self.plot_layout.setBackground('w')
        self.plot_area = DockArea()
        self.main_dock = Dock("Main plot", size=(500,200))
        self.main_dock.hideTitleBar()
        self.topoplot_dock = Dock("Topoplot", size=(250,200))
        self.m = PlotCanvas(self, width=7, height=7)
        self.topoplot_dock.addWidget(self.m)
        self.save_topoplot_btn = QPushButton("Save topoplot images")
        self.topoplot_dock.addWidget(self.save_topoplot_btn)
        self.plot_area.addDock(self.main_dock, 'left')
        self.plot_area.addDock(self.topoplot_dock, 'right', self.main_dock)
        self.topoplot_dock.hide()
        self.main_dock.addWidget(self.plot_layout)
        self.grid_rt.addWidget(self.plot_area,0,0,6,8)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(3000)
        self.slider.setValue(0)
        self.grid_rt.addWidget(self.slider, 6, 0, 1, 8)

        self.btn_open_ann_dock = QPushButton("Statistics / annotations", self)
        self.btn_open_ann_dock.setToolTip("Click to open annotations dock")
        self.grid_rt.addWidget(self.btn_open_ann_dock, 7, 0)
        self.btn_open_ann_dock.hide()

        self.button_lt_10s = QPushButton("<10", self)
        self.button_lt_10s.setToolTip("Click to go back")
        self.grid_rt.addWidget(self.button_lt_10s, 7, 1)

        self.button_lt_1s = QPushButton("<<1", self)
        self.button_lt_1s.setToolTip("Click to go back")
        self.grid_rt.addWidget(self.button_lt_1s, 7, 2)

        self.button_chg_count = QPushButton("Jump to...", self)
        self.button_chg_count.setToolTip("Click to select time for graph")
        self.grid_rt.addWidget(self.button_chg_count, 7, 3, 1, 2)

        self.button_rt_1s = QPushButton("1>>", self)
        self.button_rt_1s.setToolTip("Click to advance")
        self.grid_rt.addWidget(self.button_rt_1s, 7, 5)

        self.button_rt_10s = QPushButton("10>", self)
        self.button_rt_10s.setToolTip("Click to advance")
        self.grid_rt.addWidget(self.button_rt_10s, 7, 6)

        self.time_lbl = QLabel("0:00:00", self)
        self.grid_rt.addWidget(self.time_lbl, 7, 7)

        #---- Right side dock ----#
        self.dock_width = int(self.width * 0.23)
        # Annotation dock
        self.scroll = QDockWidget()
        self.btn_open_edit_ann = QPushButton("Open annotation editor", self)
        self.btn_open_edit_ann.setToolTip("Click to open annotation editor")
        self.scroll.setTitleBarWidget(self.btn_open_edit_ann)
        self.ann_qlist = QListWidget()
        self.scroll.setWidget(self.ann_qlist)
        self.scroll.setFloating(False)
        self.scroll.setFixedWidth(self.dock_width)

        # Annotation editor dock
        self.ann_edit_dock = QDockWidget()
        self.ann_edit_dock.setTitleBarWidget(QLabel("Annotation editor"))
        self.ann_edit_main_widget = QWidget()
        self.ann_edit_layout = QGridLayout()
        ann_txt_label = QLabel("Text: ", self)
        ann_time_label = QLabel("Time: ", self)
        ann_duration_label = QLabel("Duration: ", self)
        self.ann_txt_edit = QLineEdit(self)
        self.ann_time_edit_time = QTimeEdit(self)
        self.ann_time_edit_time.setMinimumTime(QTime(0,0,0))
        self.ann_time_edit_time.setDisplayFormat("hh:mm:ss")
        self.ann_time_edit_count = QSpinBox(self)
        self.ann_duration = QSpinBox(self)
        self.btn_ann_edit = QPushButton("Update", self)
        self.btn_ann_edit.setToolTip("Click to modify selected annotation")
        self.btn_ann_del = QPushButton("Delete", self)
        self.btn_ann_del.setToolTip("Click to delete selected annotation")
        self.btn_ann_create = QPushButton("Create", self)
        self.btn_ann_create.setToolTip("Click to create new annotation")
        self.ann_edit_layout.addWidget(ann_txt_label,0,0)
        self.ann_edit_layout.addWidget(self.ann_txt_edit,0,1,1,2)
        self.ann_edit_layout.addWidget(ann_time_label,1,0)
        self.ann_edit_layout.addWidget(self.ann_time_edit_time,1,1)
        self.ann_edit_layout.addWidget(self.ann_time_edit_count,1,2)
        self.ann_edit_layout.addWidget(ann_duration_label,2,0)
        self.ann_edit_layout.addWidget(self.ann_duration,2,1)
        self.ann_edit_layout.addWidget(self.btn_ann_edit,3,0)
        self.ann_edit_layout.addWidget(self.btn_ann_del,3,1)
        self.ann_edit_layout.addWidget(self.btn_ann_create,3,2)
        self.ann_edit_main_widget.setLayout(self.ann_edit_layout)
        self.ann_edit_main_widget.setFixedWidth(self.dock_width)
        self.ann_edit_dock.setWidget(self.ann_edit_main_widget)

        # Stats dock
        self.stats_dock = QDockWidget()
        self.btn_open_stats = QPushButton("Open signal stats", self)
        self.btn_open_stats.setToolTip("Click to open stats")
        self.stats_dock.setTitleBarWidget(self.btn_open_stats)
        self.stats_dock.setFixedWidth(self.dock_width)

        self.stats_grid = QtWidgets.QGridLayout()
        self.grid_layout = QtWidgets.QGridLayout()
        ud = 0
        all_lbl = QtWidgets.QLabel(self)
        all_lbl.setText("Overall")
        self.grid_layout.addWidget(all_lbl,ud,2,1,1)
        region_lbl = QtWidgets.QLabel(self)
        region_lbl.setText("Region")
        self.grid_layout.addWidget(region_lbl,ud,3,1,1)
        ud += 1
        mean_l = QtWidgets.QLabel(self)
        mean_l.setText("Mean:")
        self.grid_layout.addWidget(mean_l, ud, 1, 1, 1)
        self.mean_lbl = QtWidgets.QLabel(self)
        self.mean_lbl.setText("")
        self.grid_layout.addWidget(self.mean_lbl, ud, 2, 1, 1)
        self.mean_sel_lbl = QtWidgets.QLabel(self)
        self.mean_sel_lbl.setText("")
        self.grid_layout.addWidget(self.mean_sel_lbl, ud, 3, 1, 1)
        ud += 1
        var_l = QtWidgets.QLabel(self)
        var_l.setText("Var:")
        self.grid_layout.addWidget(var_l, ud, 1, 1, 1)
        self.var_lbl = QtWidgets.QLabel(self)
        self.var_lbl.setText("")
        self.grid_layout.addWidget(self.var_lbl, ud, 2, 1, 1)
        self.var_sel_lbl = QtWidgets.QLabel(self)
        self.var_sel_lbl.setText("")
        self.grid_layout.addWidget(self.var_sel_lbl, ud, 3, 1, 2)
        ud += 1
        line_len_l = QtWidgets.QLabel(self)
        line_len_l.setText("Line\nlength:")
        self.grid_layout.addWidget(line_len_l, ud, 1, 1, 1)
        self.line_len_lbl = QtWidgets.QLabel(self)
        self.line_len_lbl.setText("")
        self.grid_layout.addWidget(self.line_len_lbl, ud, 2, 1, 1)
        self.line_len_sel_lbl = QtWidgets.QLabel(self)
        self.line_len_sel_lbl.setText("")
        self.grid_layout.addWidget(self.line_len_sel_lbl, ud, 3, 1, 1)
        ud += 1
        self.grid_layout.addWidget(QHLine(), ud, 1, 1, 3)
        ud += 1
        fs_band_names = ["alpha", "beta", "gamma", "delta", "theta"]
        self.fs_band_lbls = {} # for holding fs band labels
        self.fs_band_sel_lbls = {} # for holding fs band labels for selected area
        for i, fs_band in enumerate(fs_band_names):
            lbl = QtWidgets.QLabel(self)
            lbl.setText(fs_band + ":")
            self.grid_layout.addWidget(lbl, ud + i, 1, 1, 1)
            self.fs_band_lbls[fs_band] = QtWidgets.QLabel(self)
            self.fs_band_lbls[fs_band].setText("")
            self.grid_layout.addWidget(self.fs_band_lbls[fs_band], ud + i, 2, 1, 1)
            self.fs_band_sel_lbls[fs_band] = QtWidgets.QLabel(self)
            self.fs_band_sel_lbls[fs_band].setText("")
            self.grid_layout.addWidget(self.fs_band_sel_lbls[fs_band], ud + i, 3, 1, 1)
        ud += 5
        self.qscroll = QtWidgets.QScrollArea(self)
        self.qscroll.setWidgetResizable(True)
        self.qscroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.qscroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chn_qlist = QListWidget()
        self.qscroll.setWidget(self.chn_qlist)
        self.stats_grid.addWidget(self.qscroll, 0, 0, 2, 1)
        self.stats_grid.addLayout(self.grid_layout, 0, 1)

        self.btn_add_fs_band = QPushButton("Add frequency band", self)
        self.stats_grid.addWidget(self.btn_add_fs_band,1,1)

        self.stats_main_widget = QWidget()
        self.stats_main_widget.setLayout(self.stats_grid)
        self.stats_dock.setWidget(self.stats_main_widget)

        self.scroll.hide()
        self.ann_edit_dock.hide()
        self.stats_dock.hide()
        self.addDockWidget(Qt.RightDockWidgetArea, self.scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ann_edit_dock)
        self.splitDockWidget(self.ann_edit_dock, self.scroll, Qt.Vertical)
        self.addDockWidget(Qt.RightDockWidgetArea, self.stats_dock)
        self.splitDockWidget(self.scroll, self.stats_dock, Qt.Vertical)

        #---- end right side dock ----#

        #---- end right side of screen ----#

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)
        layout.addLayout(grid_lt, 0, 0, 3, 1)
        layout.addLayout(self.grid_rt, 0, 1, 4, 3)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.set_signals_slots()
        self.init_values()

        if self.argv.show:
            self.show()
            if not self.argv.fn is None:
                self.load_data(self.argv.fn)
        else:
            fn = self.argv.fn
            self.argv_pred_fn = self.argv.predictions_file
            self.argv_mont_fn = self.argv.montage_file
            self.load_data(fn)

    def set_signals_slots(self):
        """ Sets signals and slots for the main window.
        """
        # ---- left side of the screen ---- #
        self.button_select_file.clicked.connect(self.load_data)
        self.button_chg_sig.clicked.connect(self.chg_sig)
        self.cbox_filter.toggled.connect(self.filter_checked)
        self.button_chg_filt.clicked.connect(self.change_filter)
        self.button_predict.clicked.connect(self.change_predictions)
        self.thresh_slider.sliderReleased.connect(self.change_thresh_slider)
        self.btn_topo.clicked.connect(self.minimize_topo)
        self.btn_zoom.clicked.connect(self.open_zoom_plot)
        self.button_chg_spec.clicked.connect(self.load_spec)
        self.button_amp_inc.clicked.connect(self.inc_amp)
        self.button_amp_dec.clicked.connect(self.dec_amp)
        self.ws_combobox.currentIndexChanged['int'].connect(self.chg_window_size)
        self.button_print.clicked.connect(self.print_graph)
        self.button_save_edf.clicked.connect(self.save_to_edf)
        self.btn_help.clicked.connect(self.open_help)

        # ---- right side of the screen ---- #
        self.slider.sliderReleased.connect(self.slider_change)
        self.btn_open_ann_dock.clicked.connect(self.open_ann_dock)
        self.button_lt_10s.clicked.connect(self.left_plot_10s)
        self.button_lt_1s.clicked.connect(self.left_plot_1s)
        self.button_chg_count.clicked.connect(self.get_count)
        self.button_rt_1s.clicked.connect(self.right_plot_1s)
        self.button_rt_10s.clicked.connect(self.right_plot_10s)
        self.save_topoplot_btn.clicked.connect(self.save_topoplot)

        # ---- right side dock ---- #
        self.btn_open_edit_ann.clicked.connect(self.open_ann_editor)
        self.ann_qlist.itemClicked.connect(self.ann_clicked)
        self.ann_time_edit_time.timeChanged.connect(self.update_count_time)
        self.ann_time_edit_count.valueChanged.connect(self.update_normal_time)
        self.btn_ann_edit.clicked.connect(self.ann_editor_update)
        self.btn_ann_del.clicked.connect(self.ann_editor_del)
        self.btn_ann_create.clicked.connect(self.ann_editor_create)
        self.btn_open_stats.clicked.connect(self.open_stat_window)
        self.chn_qlist.itemClicked.connect(self.stat_chn_clicked)
        self.btn_add_fs_band.clicked.connect(self.stat_add_fs_band)

    def init_values(self):
        """ Set some initial values and create Info objects.
        """
        self.count = 0  # the current location in time we are plotting
        self.init = 0  # if any data has been loaded in yet
        self.window_size = 10  # number of seconds to display at a time
        self.filter_checked = 0  # whether or not to plot filtered data
        self.ylim = [150, 100]  # ylim for unfiltered and filtered data
        self.max_channels = 70 # maximum channels you can plot at once
        self.filter_win_open = 0  # whether or not filter options window is open
        self.preds_win_open = 0  # whether or not the predictions window is open
        self.chn_win_open = 0  # whether or not the channel selection window is open
        self.organize_win_open = 0  # whether or not the signal organization window is open
        self.color_win_open = 0  # whether or not the signal colors window is open
        self.spec_win_open = 0 # whether or not the spectrogram window is open
        self.saveimg_win_open = 0 # whether or not the print preview window is open
        self.saveedf_win_open = 0 # whether or not the save edf options window is open
        self.anon_win_open = 0 # whether or not the anonymize window is open
        self.savetopo_win_open = 0 # whether or not the topoplots window is open
        self.stat_fs_band_win_open = 0 # whether or not the stat fs window is open
        self.max_time = 0  # number of seconds in the recording
        self.pi = PredsInfo()  # holds data needed to predict
        self.ci = ChannelInfo()  # holds channel information
        self.si = SpecInfo() # holds spectrogram information
        self.sii = SaveImgInfo() # holds info to save the img
        self.sei = SaveEdfInfo() # holds header for edf saving
        self.ssi = SignalStatsInfo() # holds info for stats window
        self.topoplot_line_val = 100 # holds value for topoplot line loc
        self.topoplot_line = None # topoplot line to be updated
        self.zoom_roi_pos = (0,0) # location of the roi object
        self.zoom_roi_size = (100,100) # size of the roi object
        self.zoom_roi = None # zoomROI to be updated
        self.spec_roi_val = [0,100] # size of the spec roi object
        self.spec_select_time_rect = None # the ROI to be updated

    def closeEvent(self, event):
        """ Called when the main window is closed to act as a destructor and close
            any window that is still open.
        """
        if self.filter_win_open:
            self.filter_ops.close_window()
        if self.preds_win_open:
            self.pred_ops.close_window()
        if self.chn_win_open:
            self.chn_ops.close_window()
        if self.organize_win_open:
            self.chn_org.close_window()
        if self.color_win_open:
            self.color_ops.close_window()
        if self.spec_win_open:
            self.spec_ops.close_window()
        if self.saveimg_win_open:
            self.saveimg_ops.close_window()
        if self.saveedf_win_open:
            self.saveedf_ops.close_window()
        if self.anon_win_open:
            self.anon_ops.close_window()
        if self.savetopo_win_open:
            self.savetopo_ops.close_window()
        if self.stat_fs_band_win_open:
            self.stats_fs_band_win.close_window()

        event.accept()

    def init_graph(self):
        """ Function to properly initialize everything when new data
            is loaded.
        """
        # self.init = 1 # set in load_data to prevent issues with slider
        self.fi = FilterInfo()  # holds data needed to filter
        self.filter_checked = 0  # whether or not filter checkbox is checked
        self.cbox_filter.setChecked(False)

        # check if this file is already filtered
        ann = self.edf_info.annotations
        if len(ann[0]) > 0 and ann[2][0] == "filtered":
            self.filter_checked = 1  # whether or not filter checkbox is checked
            str_lp = ann[2][1].split("Hz")[0][4:]
            str_hp = ann[2][2].split("Hz")[0][4:]
            str_n = ann[2][3].split("Hz")[0][3:]
            str_bp1 = ann[2][4].split("-")[0][4:]
            str_bp2 = ann[2][4].split("-")[1].split("Hz")[0]
            if float(str_lp) > 0:
                self.fi.lp = float(str_lp)
            else:
                self.fi.do_lp = 0
            if float(str_hp) > 0:
                self.fi.hp = float(str_hp)
            else:
                self.fi.do_hp = 0
            if float(str_n) > 0:
                self.fi.do_notch = 1
                self.fi.notch = float(str_n)
            else:
                self.fi.do_notch = 0
            if float(str_bp1) > 0 and float(str_bp2) > 0:
                self.fi.do_bp = 1
                self.fi.bp1 = float(str_bp1)
                self.fi.bp2 = float(str_bp2)
            else:
                self.fi.do_bp = 0
        else:
            self.fi.lp = self.argv.filter[1]
            self.fi.hp = self.argv.filter[2]
            self.fi.notch = self.argv.filter[3]
            self.fi.bp1 = self.argv.filter[4]
            self.fi.bp2 = self.argv.filter[5]
            self.fi.do_lp = self.fi.lp != 0
            self.fi.do_hp = self.fi.hp != 0
            self.fi.do_notch = self.fi.notch != 0
            self.fi.do_bp = self.fi.bp1 != 0 and self.fi.bp2 != 0
            if ((self.fi.do_lp or self.fi.do_hp or self.fi.do_notch or self.fi.do_bp)
                    and self.argv.filter[0] == 1):
                self.filter_checked = 1

        if self.btn_zoom.text() == "Close zoom":
            self.btn_zoom.setText("Open zoom")
            self.plot_layout.removeItem(self.zoom_plot)
            self.main_plot.removeItem(self.zoom_roi)

        if not self.topoplot_dock.isHidden():
            self.close_topoplot()

        if self.si.plot_spec:
            self.si.plot_spec = 0
            self.remove_spec_plot()
            self.si.chn_plotted = -1

        self.ylim = [150, 100]  # [150,3] # reset scale of axis
        self.window_size = self.argv.window_width # number of seconds displayed at once
        self.ws_combobox.setCurrentIndex(2)
        ind = self.ws_combobox.findText(str(self.window_size) + "s")
        if ind != -1: # -1 for not found
            self.ws_combobox.setCurrentIndex(ind)
        # self.count = 0  # current location in time
        self.ann_list = []  # list of annotations
        self.rect_list = [] # list of prediction rectangles
        self.aspan_list = []  # list of lines on the axis from preds
        self.pred_label.setText("")  # reset text of predictions
        self.thresh = self.argv.prediction_thresh  # threshold for plotting
        self.thresh_lbl.setText(
            "Change threshold of prediction:  " +
            "(threshold = " + str(self.thresh) + ")")  # reset label
        self.filtered_data = []  # set filtered_data
        self.si = SpecInfo()
    
    def load_data(self, name=""):
        """
        Function to load in the data

        loads selected .edf file into edf_info and data
        data is initially unfiltered
        """
        if self.init or self.argv.fn is None:
            name = QFileDialog.getOpenFileName(
                self, 'Open file', '.', 'EDF files (*.edf)')
            name = name[0]
        if name is None or len(name) == 0:
            return
        else:
            self.edf_file_name_temp = name
            loader = EdfLoader()
            try:
                self.edf_info_temp = loader.load_metadata(name)
            except:
                self.throw_alert("The .edf file is invalid.")
                return
            self.edf_info_temp.annotations = np.array(
                self.edf_info_temp.annotations)

            try:
                if len(self.edf_info_temp.fs) > 1:
                    self.edf_info_temp.fs = np.max(self.edf_info_temp.fs)
                elif len(self.edf_info_temp.fs) == 1:
                    self.edf_info_temp.fs = self.edf_info_temp.fs[0]
            except:
                pass

            # setting temporary variables that will be overwritten if
            # the user selects signals to plot
            self.max_time_temp = int(
                self.edf_info_temp.nsamples[0] / self.edf_info_temp.fs)
            self.ci_temp = ChannelInfo()  # holds channel information
            self.ci_temp.chns2labels = self.edf_info_temp.chns2labels
            self.ci_temp.labels2chns = self.edf_info_temp.labels2chns
            self.ci_temp.fs = self.edf_info_temp.fs
            self.ci_temp.edf_fn = name
            self.fn_full_temp = name
            if len(name.split('/')[-1]) < 40:
                self.fn_temp = name.split('/')[-1]
            else:
                self.fn_temp = name.split('/')[-1][0:37] + "..."

            self.chn_win_open = 1
            self.predicted = 0  # whether or not predictions have been made
            self.chn_ops = ChannelOptions(self.ci_temp, self)
            if self.argv.show and self.argv.montage_file is None:
                self.chn_ops.show()

    def call_initial_move_plot(self):
        """
        Function called by channel_options when channels are loaded
        """
        self.init_graph()

        self.slider.setMaximum(self.max_time - self.window_size)
        self.thresh_slider.setValue(int(self.argv.prediction_thresh * 100))

        self.ann_qlist.clear()  # Clear annotations
        self.populate_ann_dock()  # Add annotations if they exist
        self.show_ann_stats_dock()

        nchns = self.ci.nchns_to_plot
        self.plot_lines = []
        if not self.init and self.argv.location < self.max_time - self.window_size:
            self.count = self.argv.location

        ann = self.edf_info.annotations
        topo_chns_correct = self.check_topo_chns()
        if (self.pi.pred_by_chn and self.predicted and topo_chns_correct
            and not self.pi.multi_class):
            self.add_topoplot()
            self.btn_topo.setText("Hide topoplots")
            self.btn_topo.setEnabled(1)
        if self.filter_checked == 1 or (len(ann[0]) > 0 and ann[2][0] == "filtered"):
            self.move_plot(0, 0, self.ylim[1], 0)
        else:
            # profile.runctx('self.move_plot(0, 0, self.ylim[0], 0)', globals(), locals())
            self.move_plot(0, 0, self.ylim[0], 0)

        if not self.argv.save_edf_fn is None and self.init == 0:
            self.init = 1
            self.save_to_edf()

        self.init = 1

        ann = self.edf_info.annotations
        if len(ann[0]) > 0 and ann[2][0] == "filtered" or self.filter_checked == 1:
            self.cbox_filter.setChecked(True)  # must be set after init = 1

    def ann_clicked(self):
        """ Moves the plot when annotations in the dock are clicked.
        """
        loc = int(float(self.edf_info.annotations[0][self.ann_qlist.currentRow()]))
        if loc < self.max_time - self.window_size:
            self.count = loc
        else:
            self.count = self.max_time - self.window_size
        self.call_move_plot(0, 0)

        # Update annotation dock if it is open
        if self.btn_open_edit_ann.text() == "Close annotation editor":
            self.ann_txt_edit.setText(self.edf_info.annotations[2][self.ann_qlist.currentRow()])
            self.ann_time_edit_count.setValue(int(
                float(self.edf_info.annotations[0][self.ann_qlist.currentRow()])))
            self.ann_duration.setValue(int(
                float(self.edf_info.annotations[1][self.ann_qlist.currentRow()])))
            self.btn_ann_edit.setEnabled(True)
            self.btn_ann_del.setEnabled(True)

    def open_ann_editor(self):
        """ Create and open the annotation editor.
        """
        if self.btn_open_edit_ann.text() == "Open annotation editor":
            self.ann_txt_edit.clear()
            self.ann_duration.setRange(-1,self.max_time)
            self.ann_duration.setValue(-1)
            hrs, minutes, sec = convert_from_count(self.max_time)
            t = QTime(hrs, minutes, sec)
            self.ann_time_edit_time.setMaximumTime(t)
            self.ann_time_edit_count.setMaximum(self.max_time)
            self.ann_time_edit_count.setValue(self.count)
            self.btn_ann_edit.setEnabled(False)
            self.btn_ann_del.setEnabled(False)
            selected_list_items = self.ann_qlist.selectedItems()
            if len(selected_list_items) > 0:
                selected_list_items[0].setSelected(False)
            self.btn_open_edit_ann.setText("Close annotation editor")
            self.ann_edit_dock.show()
        else:
            self.btn_open_edit_ann.setText("Open annotation editor")
            self.ann_edit_dock.hide()
            if len(self.edf_info.annotations[0]) == 0:
                self.populate_ann_dock()
                self.show_ann_stats_dock()

    def open_ann_dock(self):
        """ Opens the annotation and stats dock when the button below
            plot is clicked.
        """
        self.scroll.show()
        self.stats_dock.show()
        self.stats_main_widget.hide()
        self.btn_open_ann_dock.hide()
        self.open_ann_editor()

    def populate_ann_dock(self):
        """ Fills the annotation dock with annotations if they exist.
        """
        self.ann_qlist.clear()
        ann = self.edf_info.annotations
        if len(ann[0]) > 0:
            for i in range(len(ann[0])):
                self.ann_qlist.addItem(ann[2][i])

    def show_ann_stats_dock(self):
        """ Properly show the stats and annotation dock.
        """
        ann = self.edf_info.annotations
        if len(ann[0]) == 0:
            self.ann_edit_dock.hide()
            if self.btn_open_stats.text() == "Open signal stats":
                self.scroll.hide()
                self.stats_dock.hide()
                self.btn_open_ann_dock.show()
            else:
                self.scroll.show()
                self.btn_open_ann_dock.hide()
        else:
            self.scroll.show()
            self.stats_dock.show()
            self.stats_main_widget.hide()
            self.btn_open_ann_dock.hide()

    def ann_editor_update(self):
        """ Called when the update annotation button is pressed.
        """
        ann_txt = self.ann_txt_edit.text()
        loc = self.ann_time_edit_count.value()
        dur = self.ann_duration.value()
        self.edf_info.annotations[0][self.ann_qlist.currentRow()] = loc
        self.edf_info.annotations[1][self.ann_qlist.currentRow()] = dur
        self.edf_info.annotations[2][self.ann_qlist.currentRow()] = ann_txt
        self.populate_ann_dock()
        self.call_move_plot(0,0)

    def ann_editor_del(self):
        """ Called when the delete selected annotation button is pressed.
        """
        self.edf_info.annotations = np.delete(
            self.edf_info.annotations,self.ann_qlist.currentRow(),axis = 1)
        self.btn_ann_edit.setEnabled(False)
        self.btn_ann_del.setEnabled(False)
        # self.ann_edit_dock.hide()
        self.populate_ann_dock()
        #if len(self.edf_info.annotations[0]) == 0:
        #    self.scroll.show()
        #    self.btn_open_ann_dock.hide()
        #self.ann_edit_dock.show()
        self.call_move_plot(0,0)

    def ann_editor_create(self):
        """ Called when the create new annotation button is pressed.
        """
        ann_txt = self.ann_txt_edit.text()
        if len(ann_txt) > 0:
            self.ann_txt_edit.setText("")
            loc = self.ann_time_edit_count.value()
            dur = self.ann_duration.value()
            i = 0
            while i < len(self.edf_info.annotations[0]):
                if int(float(self.edf_info.annotations[0][i])) > loc:
                    break
                i += 1
            if len(self.edf_info.annotations[0]) == 0:
                self.edf_info.annotations = np.append(
                    self.edf_info.annotations,
                    np.array([[loc], [dur], [ann_txt]]), axis = 1)
            else:
                self.edf_info.annotations = np.insert(
                    self.edf_info.annotations, i,
                    [loc, dur, ann_txt], axis = 1)
            self.populate_ann_dock()
            self.call_move_plot(0,0)

    def update_normal_time(self):
        """ Updates self.ann_time_edit_time when self.ann_time_edit_count is changed.
        """
        hrs, minutes, sec = convert_from_count(self.ann_time_edit_count.value())
        t = QTime(hrs, minutes, sec)
        self.ann_time_edit_time.setTime(t)
        self.ann_duration.setRange(-1, self.max_time - self.ann_time_edit_count.value())

    def update_count_time(self):
        """ Updates self.ann_time_edit_count when self.ann_time_edit_time is changed.
        """
        c = ( 3600 * self.ann_time_edit_time.time().hour() +
                60 * self.ann_time_edit_time.time().minute() +
                self.ann_time_edit_time.time().second() )
        self.ann_time_edit_count.setValue(c)
        self.ann_duration.setRange(-1,self.max_time - c)

    def open_zoom_plot(self):
        """ Open the zoom plot
        """
        if self.init:
            if self.btn_zoom.text() == "Open zoom":
                if self.si.plot_spec:
                    self.throw_alert("Please close the spectrogram plot before opening zoom.")
                else:
                    self.zoom_plot = self.plot_layout.addPlot(row=1, col=0, border=True)
                    self.zoom_plot.setMouseEnabled(x=False, y=False)
                    q_graphics_grid_layout = self.plot_layout.ci.layout
                    q_graphics_grid_layout.setRowStretchFactor(0, 2)
                    q_graphics_grid_layout.setRowStretchFactor(1, 1)
                    self.zoom_roi = pg.RectROI([0,0], [self.edf_info.fs * 2,200], pen=(1,9))
                    self.zoom_roi.addScaleHandle([0.5,1],[0.5,0.5])
                    self.zoom_roi.addScaleHandle([0,0.5],[0.5,0.5])
                    self.main_plot.addItem(self.zoom_roi)
                    self.zoom_roi.setZValue(2000)
                    self.zoom_roi.sigRegionChanged.connect(self.update_zoom_plot)
                    self.btn_zoom.setText("Close zoom")
                    self.zoom_plot_lines = []
                    self.zoom_rect_list = []
                    self.zoom_roi_pos = self.zoom_roi.pos()
                    self.zoom_roi_size = self.zoom_roi.size()
                    self.update_zoom_plot()
            else:
                self.btn_zoom.setText("Open zoom")
                self.plot_layout.removeItem(self.zoom_plot)
                self.main_plot.removeItem(self.zoom_roi)

    def update_zoom_plot(self):
        """ Called whenever the zoom roi is moved
        """
        self.zoom_roi_pos = self.zoom_roi.pos()
        self.zoom_roi_size = self.zoom_roi.size()

        fs = self.edf_info.fs
        nchns = self.ci.nchns_to_plot

        plot_data = np.zeros((self.ci.nchns_to_plot,self.window_size * fs))
        if self.filter_checked == 1:
            y_lim = self.ylim[1]
            self.prep_filter_ws()
            # plot_data = np.zeros(self.filtered_data.shape)
            plot_data += self.filtered_data
            stddev = np.std(
                plot_data)
            plot_data[plot_data > 3 * stddev] = 3 * stddev
            plot_data[plot_data < -3 * stddev] = -3 * stddev
        else:
            # plot_data = np.zeros(self.ci.data_to_plot.shape)
            plot_data += self.ci.data_to_plot[:,self.count * fs:(self.count + self.window_size) * fs]
            y_lim = self.ylim[0]

        if not (len(self.zoom_plot_lines) > 0 and len(self.zoom_plot_lines) == nchns):
            # self.plotWidget.clear()
            self.zoom_plot.clear()
            self.zoom_plot_lines = []
            for i in range(nchns):
                pen = pg.mkPen(color=self.ci.colors[i], width=2, style=QtCore.Qt.SolidLine)
                self.zoom_plot_lines.append(self.zoom_plot.plot(plot_data[i, :]
                             + (i + 1) * y_lim, clickable=False, pen=pen))
        else:
            for i in range(nchns):
                self.zoom_plot_lines[i].setData(plot_data[i, :]
                            + (i + 1) * y_lim)

        # add predictions
        if len(self.rect_list) > 0:
            for a in self.rect_list:
                self.zoom_plot.removeItem(a)
            self.rect_list[:] = []

        if self.predicted == 1:
            blue_brush = QBrush(QColor(38,233,254,50))
            starts, ends, chns, class_vals = self.pi.compute_starts_ends_chns(self.thresh,
                                        self.count, self.window_size, fs, nchns)
            for k in range(len(starts)):
                if self.pi.pred_by_chn and not self.pi.multi_class:
                    for i in range(nchns):
                        if chns[k][i]:
                            if i == plot_data.shape[0] - 1:
                                r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count *
                                        fs, y_lim *(i+0.5),
                                        ends[k] - starts[k], y_lim) # (x, y, w, h)
                                r1.setPen(pg.mkPen(None))
                                r1.setBrush(pg.mkBrush(color = (38,233,254,50))) # (r,g,b,alpha)
                                self.zoom_plot.addItem(r1)
                                self.rect_list.append(r1)
                            else:
                                r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count *
                                        fs, y_lim *(i + 0.5),
                                        ends[k] - starts[k], y_lim) # (x, y, w, h)
                                r1.setPen(pg.mkPen(None))
                                r1.setBrush(blue_brush) # (r,g,b,alpha)
                                self.zoom_plot.addItem(r1)
                                self.rect_list.append(r1)
                            x_vals = range(
                                int(starts[k]) - self.count * fs, int(ends[k]) - self.count * fs)
                            pen = pg.mkPen(color=self.ci.colors[i], width=3,
                                            style=QtCore.Qt.SolidLine)
                            self.plot_lines.append(self.zoom_plot.plot(x_vals,
                                                plot_data[i, int(starts[k])
                                                - self.count * fs:int(ends[k]) -
                                                self.count * fs] + i*y_lim + y_lim,
                                                clickable=False, pen=pen))
                elif not self.pi.pred_by_chn and not self.pi.multi_class:
                    r1 = pg.LinearRegionItem(values=(starts[k] - self.count * fs, ends[k]
                                    - self.count * fs),
                                    brush=blue_brush, movable=False,
                                    orientation=pg.LinearRegionItem.Vertical)
                    self.zoom_plot.addItem(r1)
                    self.rect_list.append(r1)
                elif not self.pi.pred_by_chn and self.pi.multi_class:
                    r, g, b, a = self.pi.get_color(class_vals[k])
                    brush = QBrush(QColor(r, g, b, a))
                    r1 = pg.LinearRegionItem(values=(starts[k] - self.count * fs, ends[k]
                                    - self.count * fs),
                                    brush=brush, movable=False,
                                    orientation=pg.LinearRegionItem.Vertical)
                    self.zoom_plot.addItem(r1)
                    self.rect_list.append(r1)
                else:
                    for i in range(nchns):
                        r, g, b, a = self.pi.get_color(chns[k][i])
                        brush = QBrush(QColor(r, g, b, a))
                        if i == plot_data.shape[0] - 1:
                            r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count * fs,
                                    y_lim *(i+0.5),
                                    ends[k] - starts[k], y_lim) # (x, y, w, h)
                            r1.setPen(pg.mkPen(None))
                            r1.setBrush(brush) # (r,g,b,alpha)
                            self.zoom_plot.addItem(r1)
                            self.rect_list.append(r1)
                        else:
                            r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count * fs,
                                    y_lim *(i + 0.5),
                                    ends[k] - starts[k], y_lim) # (x, y, w, h)
                            r1.setPen(pg.mkPen(None))
                            r1.setBrush(brush) # (r,g,b,alpha)
                            self.zoom_plot.addItem(r1)
                            self.rect_list.append(r1)
                        x_vals = range(
                            int(starts[k]) - self.count * fs, int(ends[k]) - self.count * fs)
                        pen = pg.mkPen(color=self.ci.colors[i], width=3, style=QtCore.Qt.SolidLine)
                        self.plot_lines.append(self.zoom_plot.plot(x_vals,
                                        plot_data[i, int(starts[k]) -
                                        self.count * fs:int(ends[k]) - self.count * fs] +
                                        i*y_lim + y_lim, clickable=False, pen=pen))


        x_ticks = []
        for i in range(self.window_size):
            x_ticks.append((i * fs, str(self.count + i)))
        x_ticks = [x_ticks]
        y_ticks = []
        for i in range(nchns + 1):
            y_ticks.append((i * y_lim, self.ci.labels_to_plot[i]))
        y_ticks = [y_ticks]

        black_pen = QPen(QColor(0,0,0))
        font = QFont()
        font.setPixelSize(16)
        self.zoom_plot.setYRange(self.zoom_roi_pos[1], self.zoom_roi_pos[1] + self.zoom_roi_size[1])
        self.zoom_plot.getAxis('left').setPen(black_pen)
        self.zoom_plot.getAxis('left').setTicks(y_ticks)
        self.zoom_plot.getAxis('left').setTextPen(black_pen)
        self.zoom_plot.getAxis("left").setStyle(tickTextOffset = 10)
        self.zoom_plot.setLabel('left', ' ', pen=(0,0,0), fontsize=20)
        self.zoom_plot.setXRange(self.zoom_roi_pos[0], self.zoom_roi_pos[0] +
                            self.zoom_roi_size[0], padding=0)
        self.zoom_plot.getAxis('bottom').setTicks(x_ticks)
        self.zoom_plot.getAxis('bottom').setTextPen(black_pen)
        self.zoom_plot.getAxis("bottom").tickFont = font
        self.zoom_plot.getAxis('bottom').setPen(black_pen)
        self.zoom_plot.setLabel('bottom', 'Time (s)', pen = black_pen)
        self.zoom_plot.getAxis('top').setWidth(200)

    def open_help(self):
        """ Called when you click the help button.
        """
        QDesktopServices.openUrl(QUrl("https://github.com/jcraley/jhu-eeg"))

    def slider_change(self):
        """ Updates plot when slider is changed.
        """
        if self.init == 1:
            size = self.slider.value()
            self.count = size + 1
            if self.count + self.window_size > self.max_time + 1:
                self.count = self.max_time - self.window_size
            self.call_move_plot(0, 1)

    def change_thresh_slider(self):
        """
        Updates the value of the threshold when the slider is changed.
        """
        val = self.thresh_slider.value()
        self.thresh = val / 100
        self.thresh_lbl.setText("Change threshold of prediction:  " +
                            "(threshold = " + str(self.thresh) + ")")
        if self.predicted == 1:
            self.call_move_plot(0, 0)

    def chg_sig(self):
        """
        Funtion to open channel_options so users can change the signals being
        plotted.
        """
        if self.init and not self.chn_win_open:
            self.chn_win_open = 1
            self.chn_ops = ChannelOptions(self.ci, self)
            self.chn_ops.show()

    def save_to_edf(self):
        """
        Opens window for anonymization. Anonymizer window calls save_sig_to_edf
        to save to file.
        """
        if self.init == 1:
            self.saveedf_win_open = 1
            self.saveedf_ops = SaveEdfOptions(self.sei, self)

    def save_sig_to_edf(self):
        """
        Function to save current data to .edf file, called by anonymization windows
        """
        if self.init == 1:
            if self.filter_checked == 1:
                data_to_save = filter_data(
                    self.ci.data_to_plot, self.edf_info.fs, self.fi)
                if self.fi.filter_canceled == 1:
                    self.fi.filter_canceled = 0
                    return
            else:
                data_to_save = self.ci.data_to_plot

            # write annotations
            ann = self.edf_info.annotations
            if len(ann[0]) > 0 and ann[2][0] == "filtered":
                self.throw_alert("If filter values have since been changed, " +
                                "filter history will not be saved.\n"  +
                                "If you would like to append some record of " +
                                "previous filters, please add an annotation.")
            if self.argv.save_edf_fn is None:
                file = QFileDialog.getSaveFileName(self, 'Save File')
                file = file[0]
            else:
                file = self.argv.save_edf_fn

            nchns = self.ci.nchns_to_plot
            labels = self.ci.labels_to_plot

            # if predictions, save them as well
            if self.predicted == 1:
                if self.pi.pred_by_chn:
                    saved_edf = pyedflib.EdfWriter(file + '.edf', nchns * 2)
                else:
                    saved_edf = pyedflib.EdfWriter(file + '.edf', nchns + 1)
            else:
                saved_edf = pyedflib.EdfWriter(file + '.edf', nchns)

            self.sei.convert_to_header()
            saved_edf.setHeader(self.sei.pyedf_header)
            # Set fs and physical min/max
            fs = self.edf_info.fs
            for i in range(nchns):
                saved_edf.setPhysicalMaximum(i, np.max(data_to_save[i]))
                saved_edf.setPhysicalMinimum(i, np.min(data_to_save[i]))
                saved_edf.setSamplefrequency(i, fs)
                saved_edf.setLabel(i, labels[i + 1])
            # if predictions, save them as well
            if self.predicted == 1:
                temp = []
                for i in range(nchns):
                    temp.append(data_to_save[i])
                if self.pi.pred_by_chn:
                    for i in range(nchns):
                        saved_edf.setPhysicalMaximum(nchns + i, 1)
                        saved_edf.setPhysicalMinimum(nchns + i, 0)
                        saved_edf.setSamplefrequency(
                            nchns + i, fs / self.pi.pred_width)
                        saved_edf.setLabel(nchns + i, "PREDICTIONS_" + str(i))
                    for i in range(nchns):
                        temp.append(self.pi.preds_to_plot[:, i])
                else:
                    saved_edf.setPhysicalMaximum(nchns, 1)
                    saved_edf.setPhysicalMinimum(nchns, 0)
                    saved_edf.setSamplefrequency(nchns, fs / self.pi.pred_width)
                    saved_edf.setLabel(nchns, "PREDICTIONS")
                    temp.append(self.pi.preds_to_plot)
                data_to_save = temp

            saved_edf.writeSamples(data_to_save)

            # write annotations
            if len(ann[0]) > 0 and ann[2][0] == "filtered":
                for aa in range(5): # remove any old annotations
                    ann = np.delete(ann, 0, axis=1)
            if self.filter_checked == 1:
                if len(ann[0]) == 0:
                    ann = np.array([0.0, -1.0, "filtered"])
                    ann = ann[..., np.newaxis]
                else:
                    ann = np.insert(ann, 0, [0.0, -1.0, "filtered"], axis=1)
                str_filt = ""
                str_filt += "LP: " + str(self.fi.do_lp * self.fi.lp) + "Hz"
                ann = np.insert(ann, 1, [0.0, -1.0, str_filt], axis=1)
                str_filt = "" + "HP: " + str(self.fi.do_hp * self.fi.hp) + "Hz"
                ann = np.insert(ann, 2, [0.0, -1.0, str_filt], axis=1)
                str_filt = "" + "N: " + str(self.fi.do_notch * self.fi.notch) + "Hz"
                ann = np.insert(ann, 3, [0.0, -1.0, str_filt], axis=1)
                str_filt = ("" + "BP: " + str(self.fi.do_bp * self.fi.bp1) + "-" +
                                str(self.fi.do_bp * self.fi.bp2) + "Hz")
                ann = np.insert(ann, 4, [0.0, -1.0, str_filt], axis=1)
                # ann = np.insert(ann, 1, [0.0, -1.0, str_filt], axis=1)
            for i in range(len(ann[0])):
                saved_edf.writeAnnotation(
                    float(ann[0][i]), float((ann[1][i])), ann[2][i])

            # Close file
            saved_edf.close()

            # if you are just saving to edf, close the window
            if not self.argv.save_edf_fn is None:
                self.argv.save_edf_fn = None
                if self.argv.show == 0:
                    sys.exit()

    def right_plot_1s(self):
        """ Move plot right 1s """
        self.call_move_plot(1, 1)

    def left_plot_1s(self):
        """ Move plot left 1s """
        self.call_move_plot(0, 1)

    def right_plot_10s(self):
        """ Move plot right 10s """
        self.call_move_plot(1, 10)

    def left_plot_10s(self):
        """ Move plot left 10s """
        self.call_move_plot(0, 10)

    def inc_amp(self):
        """ Increase amplitude """
        if self.init == 1:
            if self.ylim[0] > 50:
                self.ylim[0] = self.ylim[0] - 15
                self.ylim[1] = self.ylim[1] - 10
                self.call_move_plot(0, 0)

    def dec_amp(self):
        """ Decrease amplitude """
        if self.init == 1:
            if self.ylim[0] < 250:
                self.ylim[0] = self.ylim[0] + 15
                self.ylim[1] = self.ylim[1] + 10
                self.call_move_plot(0, 0)

    def chg_window_size(self):
        """ Change window size """
        if self.init == 1:
            new_ws = self.ws_combobox.currentText()
            new_ws = int(new_ws.split("s")[0])
            self.window_size = new_ws
            self.slider.setMaximum(self.max_time - self.window_size)
            if self.count > self.max_time - self.window_size:
                self.count = self.max_time - self.window_size
            self.call_move_plot(0, 0)
        else:
            self.ws_combobox.setCurrentIndex(2)

    def get_count(self):
        """ Used for the "jump to" button to update self.count to the user's input
        """
        if self.init == 1:
            num, ok = QInputDialog.getInt(self, "Jump to...", "Enter a time in seconds:",
                                          0, 0, self.max_time)
            if ok:
                if num > self.max_time - self.window_size:
                    num = self.max_time - self.window_size
                self.count = num
                self.call_move_plot(0, 0)

    def print_graph(self):
        """ Save the graph as a figure """
        if self.init and self.saveimg_win_open == 0:
            self.call_move_plot(0, 0, 1)
            self.saveimg_win_open = 1
            self.saveimg_ops = SaveImgOptions(self.sii, self)
            self.saveimg_ops.show()

    def call_move_plot(self, right, num_move, print_graph=0):
        """ Helper function to call move_plot for various buttons.
        """
        if self.init == 1:
            if self.filter_checked == 1:
                self.move_plot(right, num_move, self.ylim[1], print_graph)
            else:
                self.move_plot(right, num_move, self.ylim[0], print_graph)

    def move_plot(self, right, num_move, y_lim, print_graph):
        """
        Function to shift the graph left and right

        Args:
            right -  0 for left, 1 for right
            num_move - integer in seconds to move by
            y_lim - the values for the y_limits of the plot
            print_graph - whether or not to print a copy of the graph
        """
        black_pen = QPen(QColor(0,0,0),3)
        fs = self.edf_info.fs
        if not self.argv.predictions_file is None and self.init == 0:
            self.predicted = 1
            self.pi.set_preds(self.argv.predictions_file, self.max_time,
                              fs, self.ci.nchns_to_plot)
            self.pi.preds_to_plot = self.pi.preds

        if right == 0 and self.count - num_move >= 0:
            self.count = self.count - num_move
        elif (right == 1 and (self.count + num_move +
                self.window_size <= self.ci.data_to_plot.shape[1] / fs)):
            self.count = self.count + num_move
        self.slider.setValue(self.count)
        t = get_time(self.count)
        self.time_lbl.setText(t)

        plot_data = np.zeros((self.ci.nchns_to_plot,self.window_size * fs))
        if self.filter_checked == 1:
            self.prep_filter_ws()
            # plot_data = np.zeros(self.filtered_data.shape)
            plot_data += self.filtered_data
            stddev = np.std(plot_data)
            plot_data[plot_data > 3 * stddev] = 3 * stddev  # float('nan') # clip amplitude
            plot_data[plot_data < -3 * stddev] = -3 * stddev
        else:
            plot_data += self.ci.data_to_plot[:,self.count * fs:(self.count + self.window_size) * fs]
            stddev = np.std(plot_data)
            plot_data[plot_data > 5 * stddev] = 5 * stddev  # float('nan') # clip amplitude
            plot_data[plot_data < -5 * stddev] = -5 * stddev

        nchns = self.ci.nchns_to_plot
        if self.predicted == 1:
            self.pred_label.setText("Predictions plotted.")
        else:
            self.pred_label.setText("")

        if not (len(self.plot_lines) > 0 and len(self.plot_lines) == nchns):
            # self.plotWidget.clear()
            self.main_plot.clear()
            self.plot_lines = []
            for i in range(nchns):
                pen = pg.mkPen(color=self.ci.colors[i], width=2, style=QtCore.Qt.SolidLine)
                self.plot_lines.append(self.main_plot.plot(plot_data[i, :]
                             + (i + 1) * y_lim, clickable=False, pen=pen))
        else:
            for i in range(nchns):
                self.plot_lines[i].setData(plot_data[i, :]
                            + (i + 1) * y_lim)

        # add predictions
        if len(self.rect_list) > 0:
            for a in self.rect_list:
                self.main_plot.removeItem(a)
            self.rect_list[:] = []

        width = 1 / (nchns + 2)
        if self.predicted == 1:
            blue_brush = QBrush(QColor(38,233,254,50))
            starts, ends, chns, class_vals = self.pi.compute_starts_ends_chns(self.thresh,
                                        self.count, self.window_size, fs, nchns)
            for k in range(len(starts)):
                if self.pi.pred_by_chn and not self.pi.multi_class:
                    for i in range(nchns):
                        if chns[k][i]:
                            if i == plot_data.shape[0] - 1:
                                r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count *
                                        fs, y_lim *(i+0.5),
                                        ends[k] - starts[k], y_lim) # (x, y, w, h)
                                r1.setPen(pg.mkPen(None))
                                r1.setBrush(pg.mkBrush(color = (38,233,254,50))) # (r,g,b,alpha)
                                self.main_plot.addItem(r1)
                                self.rect_list.append(r1)
                            else:
                                r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count *
                                        fs, y_lim *(i + 0.5),
                                        ends[k] - starts[k], y_lim) # (x, y, w, h)
                                r1.setPen(pg.mkPen(None))
                                r1.setBrush(blue_brush) # (r,g,b,alpha)
                                self.main_plot.addItem(r1)
                                self.rect_list.append(r1)
                            x_vals = range(
                                int(starts[k]) - self.count * fs, int(ends[k]) - self.count * fs)
                            pen = pg.mkPen(color=self.ci.colors[i], width=3,
                                            style=QtCore.Qt.SolidLine)
                            self.plot_lines.append(self.main_plot.plot(x_vals, plot_data[i,
                                                int(starts[k]) - self.count * fs:int(ends[k]) -
                                                self.count * fs] + i*y_lim + y_lim,
                                                clickable=False, pen=pen))
                elif not self.pi.pred_by_chn and not self.pi.multi_class:
                    r1 = pg.LinearRegionItem(values=(starts[k] - self.count * fs,
                                    ends[k] - self.count * fs),
                                    brush=blue_brush, movable=False,
                                    orientation=pg.LinearRegionItem.Vertical)
                    self.main_plot.addItem(r1)
                    self.rect_list.append(r1)
                elif not self.pi.pred_by_chn and self.pi.multi_class:
                    r, g, b, a = self.pi.get_color(class_vals[k])
                    brush = QBrush(QColor(r, g, b, a))
                    r1 = pg.LinearRegionItem(values=(starts[k] - self.count * fs,
                                    ends[k] - self.count * fs),
                                    brush=brush, movable=False,
                                    orientation=pg.LinearRegionItem.Vertical)
                    self.main_plot.addItem(r1)
                    self.rect_list.append(r1)
                else:
                    for i in range(nchns):
                        r, g, b, a = self.pi.get_color(chns[k][i])
                        brush = QBrush(QColor(r, g, b, a))
                        if i == plot_data.shape[0] - 1:
                            r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count * fs,
                                    y_lim *(i+0.5),
                                    ends[k] - starts[k], y_lim) # (x, y, w, h)
                            r1.setPen(pg.mkPen(None))
                            r1.setBrush(brush) # (r,g,b,alpha)
                            self.main_plot.addItem(r1)
                            self.rect_list.append(r1)
                        else:
                            r1 = pg.QtGui.QGraphicsRectItem(starts[k] - self.count * fs,
                                    y_lim *(i + 0.5),
                                    ends[k] - starts[k], y_lim) # (x, y, w, h)
                            r1.setPen(pg.mkPen(None))
                            r1.setBrush(brush) # (r,g,b,alpha)
                            self.main_plot.addItem(r1)
                            self.rect_list.append(r1)
                        x_vals = range(int(starts[k]) - self.count * fs,
                                       int(ends[k]) - self.count * fs)
                        pen = pg.mkPen(color=self.ci.colors[i], width=3,
                                    style=QtCore.Qt.SolidLine)
                        self.plot_lines.append(self.main_plot.plot(x_vals,
                                        plot_data[i, int(starts[k]) -
                                        self.count * fs:int(ends[k]) - self.count * fs]
                                        + i * y_lim + y_lim, clickable=False, pen=pen))


        step_size = fs  # Updating the x labels with scaling
        step_width = 1
        if self.window_size >= 15 and self.window_size <= 25:
            step_size = step_size * 2
            step_width = step_width * 2
        elif self.window_size > 25:
            step_size = step_size * 3
            step_width = step_width * 3
        x_ticks = []
        spec_x_ticks = []
        for i in range(int(self.window_size / step_width) + 1):
            x_ticks.append((i * step_size, str(self.count + i * step_width)))
            spec_x_ticks.append((i * step_width, str(self.count + i * step_width)))
        x_ticks = [x_ticks]
        spec_x_ticks = [spec_x_ticks]

        y_ticks = []
        for i in range(nchns + 1):
            y_ticks.append((i * y_lim, self.ci.labels_to_plot[i]))
        y_ticks = [y_ticks]

        font = QFont()
        font.setPixelSize(16)

        self.main_plot.setYRange(-y_lim, (nchns + 1) * y_lim)
        self.main_plot.getAxis('left').setStyle(tickFont = font)
        self.main_plot.getAxis('left').setTextPen(black_pen)
        self.main_plot.getAxis('left').setTicks(y_ticks)
        self.main_plot.getAxis("left").setStyle(tickTextOffset = 10)
        self.main_plot.setLabel('left', ' ', pen=(0,0,0), fontsize=20)
        # self.main_plot.getAxis("left").setScale(y_lim * (nchns + 2))

        self.main_plot.setXRange(0 * fs, (0 + self.window_size) * fs, padding=0)
        self.main_plot.getAxis('bottom').setTicks(x_ticks)
        self.main_plot.getAxis('bottom').setStyle(tickFont = font)
        self.main_plot.getAxis('bottom').setTextPen(black_pen)
        self.main_plot.setLabel('bottom', 'Time (s)', pen = black_pen)
        self.main_plot.getAxis('top').setWidth(200)

        # add annotations
        if len(self.ann_list) > 0:
            for a in self.ann_list:
                self.main_plot.removeItem(a)
            self.ann_list[:] = []
        ann, idx_w_ann = check_annotations(self.count, self.window_size, self.edf_info)
        font_size = 10
        if len(ann) != 0:
            ann = np.array(ann).T
            txt = ""
            int_prev = int(float(ann[0, 0]))
            for i in range(ann.shape[1]):
                int_i = int(float(ann[0, i]))
                if int_prev == int_i:
                    txt = txt + "\n" + ann[2, i]
                else:
                    if idx_w_ann[int_prev - self.count] and int_prev % 2 == 1:
                        txt_item = pg.TextItem(text=txt, color='k', anchor=(0,1))
                        self.main_plot.addItem(txt_item)
                        txt_item.setPos((int_prev - self.count)*fs, -(3/2)*y_lim)
                        self.ann_list.append(txt_item)
                    else:
                        txt_item = pg.TextItem(text=txt, color='k', anchor=(0,1))
                        self.main_plot.addItem(txt_item)
                        txt_item.setPos((int_prev - self.count)*fs, -y_lim)
                        self.ann_list.append(txt_item)
                    txt = ann[2, i]
                int_prev = int_i
            if txt != "":
                if idx_w_ann[int_i - self.count] and int_i % 2 == 1:
                    txt_item = pg.TextItem(text=txt, color='k', anchor=(0,1))
                    self.main_plot.addItem(txt_item)
                    txt_item.setPos((int_i - self.count)*fs, -(3 / 2) *y_lim)
                    self.ann_list.append(txt_item)
                else:
                    txt_item = pg.TextItem(text=txt, color='k', anchor=(0,1))
                    self.main_plot.addItem(txt_item)
                    txt_item.setPos((int_i - self.count)*fs, -y_lim)
                    self.ann_list.append(txt_item)

        if print_graph == 1 or (not self.argv.export_png_file is None and self.init == 0):
            # exporter = pg.exporters.ImageExporter(self.plotWidget.scene())
            # exporter.export(file[0] + '.png')
            self.sii.data = plot_data
            self.sii.pi = self.pi
            self.sii.ci = self.ci
            self.sii.predicted = self.predicted
            self.sii.fs = fs
            self.sii.count = self.count
            self.sii.window_size = self.window_size
            self.sii.y_lim = y_lim
            self.sii.thresh = self.thresh
        if not self.argv.export_png_file is None and self.init == 0:
            self.saveimg_win_open = 1
            self.saveimg_ops = SaveImgOptions(self.sii, self)


        # update the topoplot
        if not self.topoplot_dock.isHidden():
            plot_val = self.topoplot_line.value() + self.count * fs
            pred_loc = plot_val / self.pi.pred_width
            self.update_topoplot(int(pred_loc))
            # need to redraw each time, because if there are preds
            # and you do not redraw the line will not be shown
            if not self.topoplot_line is None:
                self.main_plot.removeItem(self.topoplot_line)
            self.topoplot_line = pg.InfiniteLine(pos=self.topoplot_line_val,
                                    angle=90, movable=True,pen=black_pen)
            self.topoplot_line.sigPositionChanged.connect(self.update_topoplot_line)
            self.main_plot.addItem(self.topoplot_line)
            self.topoplot_line.setZValue(2000)

        if self.si.plot_spec:
            redBrush = QBrush(QColor(217, 43, 24,50))
            if not self.spec_select_time_rect is None:
                self.main_plot.removeItem(self.spec_select_time_rect)
            self.spec_select_time_rect = pg.LinearRegionItem(
                        values=(self.spec_roi_val[0], self.spec_roi_val[1]),
                        brush=redBrush, movable=True,
                        orientation=pg.LinearRegionItem.Vertical)
            self.spec_select_time_rect.setSpan((self.si.chn_plotted + 2) / (nchns + 3),
                        (self.si.chn_plotted + 3) / (nchns + 3))
            self.spec_select_time_rect.setBounds([0,fs * self.window_size])
            self.main_plot.addItem(self.spec_select_time_rect)
            self.spec_select_time_rect.sigRegionChangeFinished.connect(self.spec_time_select_changed)
            # dataForSpec = self.si.data
            # f, t, Sxx = scipy.signal.spectrogram(
            # self.si.data[self.count * fs:(self.count + self.window_size) * fs],
            # fs=fs, nperseg=fs, noverlap=0)
            # Fit the min and max levels of the histogram to the data available
            # self.hist.axis.setPen(black_pen)
            # self.hist.setLevels(0,200)#np.min(Sxx), np.max(Sxx))
            # This gradient is roughly comparable to the gradient used by Matplotlib
            # You can adjust it and then save it using hist.gradient.saveState()
            # self.hist.gradient.restoreState(
            #     {'mode': 'rgb',
            #     'ticks': [(0.5, (0, 182, 188, 255)),
            #            (1.0, (246, 111, 0, 255)),
            #            (0.0, (75, 0, 113, 255))]})
            # Sxx contains the amplitude for each pixel
            # self.img.setImage(Sxx)
            # Scale the X and Y Axis to time and frequency (standard is pixels)
            # self.img.scale(self.window_size/np.size(Sxx, axis=1),
            #         f[-1]/np.size(Sxx, axis=0))
            # Limit panning/zooming to the spectrogram
            # self.specPlot.setLimits(xMin=0, xMax=self.window_size,
            # yMin=self.si.min_fs, yMax=self.si.max_fs)
            self.spec_time_select_changed()
            self.specPlot.getAxis('bottom').setTextPen(black_pen)
            # self.specPlot.getAxis('bottom').setTicks(spec_x_ticks)
            # Add labels to the axis
            self.specPlot.setLabel('bottom', "Frequency", units='Hz')
            # pyqtgraph automatically scales the axis and adjusts
            # the SI prefix (in this case kHz)
            self.specPlot.getAxis('left').setTextPen(black_pen)
            self.specPlot.setLabel('left', "PSD", units='log(V**2/Hz)')
            self.specPlot.setXRange(self.si.min_fs,self.si.max_fs,padding=0)
            self.specPlot.setLogMode(False, True)
            # self.specPlot.setYRange(self.si.min_fs,self.si.max_fs,padding=0)
            self.specPlot.setTitle(self.si.chn_name,color='k',size='16pt')
        if self.btn_zoom.text() == "Close zoom":
            # need to redraw each time, because if there are preds
            # and you do not redraw the roi will not be shown
            if not self.zoom_roi is None:
                self.main_plot.removeItem(self.zoom_roi)
            self.zoom_roi = pg.RectROI([self.zoom_roi_pos[0],self.zoom_roi_pos[1]],
                                        [self.zoom_roi_size[0],self.zoom_roi_size[1]], pen=(1,9))
            self.zoom_roi.addScaleHandle([0.5,1],[0.5,0.5])
            self.zoom_roi.addScaleHandle([0,0.5],[0.5,0.5])
            self.main_plot.addItem(self.zoom_roi)
            self.zoom_roi.setZValue(2000)
            self.zoom_roi.sigRegionChanged.connect(self.update_zoom_plot)
            self.update_zoom_plot()
        if self.btn_open_stats.text() == "Close signal stats":
            self.stat_time_select_changed()

        if self.init == 0 and self.argv.show:
            self.throw_alert("Data has been plotted.")

    def minimize_topo(self):
        """ Function to minimize topoplot.
        """
        if self.btn_topo.text() == "Show topoplots":
            # show them, call move plot
            self.btn_topo.setText("Hide topoplots")
            self.add_topoplot()
            self.call_move_plot(0,0)
        else:
            # hide them, call move plot
            self.btn_topo.setText("Show topoplots")
            self.close_topoplot()
            self.call_move_plot(0,0)

    def close_topoplot(self):
        """ Function to close the topoplot.
        """
        self.topoplot_dock.hide()
        self.main_plot.removeItem(self.topoplot_line)

    def add_topoplot(self):
        """ Function called when pred options loads and pred_by_chn == 1
        """
        self.topoplot_dock.show()
        black_pen = QPen(QColor(0,0,0))
        self.topoplot_line = pg.InfiniteLine(pos=self.edf_info.fs,
                                angle=90, movable=True,pen=black_pen)
        self.main_plot.addItem(self.topoplot_line)
        self.topoplot_line.setZValue(2000)

    def update_topoplot(self, pred_loc):
        """ Update the topoplot if pred_by_chn == 1

            Args:
                pred_loc: the index of the slice in time to plot
        """
        # clear figure
        self.m.fig.clf()

        curr_score = self.pi.preds_to_plot[pred_loc,:]
        # Create the layout
        layout = mne.channels.read_layout('EEG1005')
        pos2d = []
        layout_names = [name.upper() for name in layout.names]
        for ch in reversed(self.ci.labels_to_plot):
            if ch != "Notes":
                if '-' in ch:
                    anode, cathode = ch.split('-')
                    anode_idx = layout_names.index(anode)
                    cathode_idx = layout_names.index(cathode)
                    anode_pos = layout.pos[anode_idx, 0:2]
                    cathode_pos = layout.pos[cathode_idx, 0:2]
                    pos2d.append([(a + c) / 2 for a, c in zip(anode_pos, cathode_pos)])
                else:
                    idx = layout_names.index(ch)
                    pos2d.append(layout.pos[idx, 0:2])
        pos2d = np.asarray(pos2d)
        # Scale locations from [-1, 1]
        pos2d = 2 * (pos2d - 0.5)

        self.ax = self.m.fig.add_subplot(self.m.gs[0])
        im, cn = mne.viz.plot_topomap(curr_score, pos2d, sphere=1,
                                  axes=self.ax, vmin=0, vmax=1, show=False,
                                  outlines='head')
        self.m.draw()

    def update_topoplot_line(self):
        """ Called whenever the topoplot line is moved.
        """
        # get the actual location in nsamples
        plot_val = self.topoplot_line.value() + self.count * self.edf_info.fs
        # convert this to prediction value
        pred_loc = plot_val / self.pi.pred_width
        old_pred_loc = self.topoplot_line_val + self.count * self.edf_info.fs
        old_pred_loc = old_pred_loc / self.pi.pred_width
        # only update the plot if in a new location
        if pred_loc != old_pred_loc:
            self.update_topoplot(int(pred_loc))
        self.topoplot_line_val = self.topoplot_line.value()

    def check_topo_chns(self):
        """ Function to check whether channels to plot
            has the proper channels or not. Must be same
            as bip1020 or ar1020.

            Returns:
                1 if the channels are correct, 0 otherwise
        """
        ret = 1
        for ch in self.ci.labels_to_plot:
            if not ch in self.ci.labelsBIP1020 and ch != "Notes":
                ret = 0
        if ret == 0:
            ret = 1
        else:
            return ret

        for ch in self.ci.labels_to_plot:
            if not ch in self.ci.labelsAR1020 and ch != "Notes":
                ret = 0
        return ret

    def save_topoplot(self):
        """ Opens the window to save the topoplot.
            Save figures for what is currently on screen.
        """
        self.savetopo_ops = SaveTopoplotOptions(self)
        self.savetopo_win_open = 1

    def filter_checked(self):
        """ Function for when the filterbox is checked

        sets self.filter_checked to the appropriate value, generates filtered_data
        if needed and re-plots data with the correct type

        prevents the filter box from being able to be checked before data is loaded
        """
        cbox = self.sender()

        if self.init == 1:
            fs = self.edf_info.fs
            if cbox.isChecked():
                self.filter_checked = 1
            else:
                self.filter_checked = 0
            # if you start / stop filtering, need to update the stats
            if self.btn_open_stats.text() == "Close signal stats":
                self.stat_chn_clicked()
            # if data was already filtered do not uncheck box
            ann = self.edf_info.annotations
            if len(ann[0]) > 0 and ann[2][0] == "filtered":
                self.filter_checked = 1
                cbox.setChecked(True)
            self.call_move_plot(1, 0)
        elif self.init == 0 and cbox.isChecked():
            cbox.setChecked(False)

    def prep_filter_ws(self):
        """ Does filtering for one window of size window_size
        """
        fs = self.edf_info.fs
        if (len(self.filtered_data) == 0 or
                (self.filtered_data.shape !=
                self.ci.data_to_plot[:,self.count*fs:(self.count +
                self.window_size)*fs].shape)):
            self.filtered_data = np.zeros((self.ci.nchns_to_plot,self.window_size * fs))
        filt_window_size = filter_data(
            self.ci.data_to_plot[:, self.count * fs:(self.count + self.window_size)*fs],
                            fs, self.fi)
        filt_window_size = np.array(filt_window_size)
        self.filtered_data = filt_window_size

    def change_filter(self):
        """ Opens the FilterOptions window
        """
        if self.init == 1:
            self.filter_win_open = 1
            self.filter_ops = FilterOptions(self.fi, self)
            self.filter_ops.show()

    def change_predictions(self):
        """ Take loaded model and data and compute predictions
        """
        if self.init == 1:
            self.preds_win_open = 1
            self.pred_ops = PredictionOptions(self.pi, self)
            self.pred_ops.show()

    def make_spec_plot(self):
        """ Creates the spectrogram plot.
        """
        self.specPlot = self.plot_layout.addPlot(row=1, col=0)
        fs = self.edf_info.fs
        f, Pxx_den = signal.welch(self.si.data[(1) * fs:(4) * fs], fs)
        self.specPlot.clear()
        self.spec_plot_lines = []
        pen = QPen(QColor(0,0,0))
        self.spec_plot_lines.append(self.specPlot.plot(f,Pxx_den, clickable=False, pen=pen))


        self.specPlot.setMouseEnabled(x=False, y=False)
        qGraphicsGridLayout = self.plot_layout.ci.layout
        qGraphicsGridLayout.setRowStretchFactor(0, 2)
        qGraphicsGridLayout.setRowStretchFactor(1, 1)
        # pg.setConfigOptions(imageAxisOrder='row-major')
        # self.img = pg.ImageItem() # Item for displaying image data
        # self.specPlot.addItem(self.img)
        # self.hist = pg.HistogramLUTItem()
        # Add a histogram with which to control the gradient of the image
        # self.hist.setImageItem(self.img)
        # # Link the histogram to the image
        # self.plot_layout.addItem(self.hist, row = 1, col = 1)
        # To make visible, add the histogram
        # self.hist.setLevels(0,200)
        #redBrush = QBrush(QColor(217, 43, 24,50))
        #nchns = self.ci.nchns_to_plot
        #self.spec_select_time_rect = pg.LinearRegionItem(values=(fs, 4 * fs),
        #                brush=redBrush, movable=True,
        #                orientation=pg.LinearRegionItem.Vertical)
        #self.spec_select_time_rect.setSpan((self.si.chn_plotted + 2) / (nchns + 3),
        #                (self.si.chn_plotted + 3) / (nchns + 3))
        #self.spec_select_time_rect.setBounds([0,fs * self.window_size])
        #self.main_plot.addItem(self.spec_select_time_rect)
        #self.spec_select_time_rect.sigRegionChangeFinished.connect(self.spec_time_select_changed)

    def spec_time_select_changed(self):
        """ Function called when the user changes the region that selects where in
            time to compute the power spectrum
        """
        fs = self.edf_info.fs
        bounds = self.spec_select_time_rect.getRegion()
        self.spec_roi_val[0] = bounds[0]
        self.spec_roi_val[1] = bounds[1]
        if self.spec_roi_val[0] < 0:
            self.spec_roi_val[0] = 0
        if self.spec_roi_val[1] > self.window_size * fs:
            self.spec_roi_val[1] = (self.window_size - 1) * fs
        if self.spec_roi_val[0] >= self.spec_roi_val[1]:
            self.spec_roi_val[1] = 100 + self.spec_roi_val[0]

        self.spec_select_time_rect.setRegion((self.spec_roi_val[0], self.spec_roi_val[1]))
        bounds = bounds + self.count * fs
        # f, Pxx_den = signal.welch(self.si.data[int(bounds[0]):int(bounds[1])], fs)
        f, Pxx_den = signal.periodogram(self.si.data[int(bounds[0]):int(bounds[1])], fs)
        pen = pg.mkPen(color=(178, 7, 245), width=3, style=QtCore.Qt.SolidLine)
        # pen = pg.mkPen(color=self.ci.colors[i], width=2, style=QtCore.Qt.SolidLine)
        self.spec_plot_lines[0].setData(f[1:],Pxx_den[1:], clickable=False, pen=pen)

    def update_spec_chn(self):
        """ Updates spectrogram plot.
        """
        self.main_plot.removeItem(self.spec_select_time_rect)
        redBrush = QBrush(QColor(217, 43, 24,50))
        nchns = self.ci.nchns_to_plot
        fs = self.edf_info.fs
        self.spec_select_time_rect = pg.LinearRegionItem(values=(fs, 4 * fs),
                        brush=redBrush, movable=True,
                        orientation=pg.LinearRegionItem.Vertical)
        self.spec_select_time_rect.setSpan((self.si.chn_plotted + 2) / (nchns + 3),
                                    (self.si.chn_plotted + 3) / (nchns + 3))
        self.main_plot.addItem(self.spec_select_time_rect)
        self.spec_select_time_rect.sigRegionChangeFinished.connect(self.spec_time_select_changed)

    def remove_spec_plot(self):
        """ Removes the spectrogram plot.
        """
        self.plot_layout.removeItem(self.specPlot)
        # self.plot_layout.removeItem(self.hist)
        self.main_plot.removeItem(self.spec_select_time_rect)

    def load_spec(self):
        """ Opens the SpecOptions window
        """
        if self.init == 1:
            if self.btn_zoom.text() == "Close zoom":
                self.throw_alert("Please close the zoom plot before opening the spectrogram.")
            else:
                self.spec_win_open = 1
                self.spec_ops = SpecOptions(self.si, self)
                self.spec_ops.show()

    def open_stat_window(self):
        """ Opens the statistics window in the sidebar.
        """
        if self.btn_open_stats.text() == "Open signal stats":
            self.btn_open_stats.setText("Close signal stats")
            self.stats_main_widget.show()
            self.populate_stat_list()
            self.chn_qlist.setCurrentRow(0)
            self.ssi.chn = 0
            self.create_stat_select_time_rect(self.ssi.chn)
            self.stat_chn_clicked()
        else:
            self.btn_open_stats.setText("Open signal stats")
            self.remove_stat_select_time_rect()
            self.stats_main_widget.hide()
            if self.btn_open_edit_ann.text() == "Open annotation editor":
                self.populate_ann_dock()
                self.show_ann_stats_dock()

    def populate_stat_list(self):
        """ Fill the stats window with channels.
        """
        # Remove old channels if they exist
        self.chn_qlist.clear()
        chns = self.ci.labels_to_plot
        self.ssi.chn_items = []
        for i in range(1, len(chns)):
            self.ssi.chn_items.append(QListWidgetItem(chns[i], self.chn_qlist))
            self.chn_qlist.addItem(self.ssi.chn_items[i - 1])

    def stat_add_fs_band(self):
        """ Opens the window to add new fs bands.
        """
        self.stat_fs_band_win_open = 1
        self.stats_fs_band_win = SignalStatsOptions(self.ssi, self)

    def stat_chn_clicked(self):
        """ When a channel is clicked.
        """
        self.remove_stat_select_time_rect()
        self.ssi.chn = self.chn_qlist.currentRow()
        self.create_stat_select_time_rect(self.ssi.chn)
        mean_str, var_str, line_len_str = self.get_stats(0,self.max_time * self.edf_info.fs)

        mean_str = "" + "{:.2f}".format(mean_str)
        self.mean_lbl.setText(mean_str)

        var_str = "" + "{:.2f}".format(var_str)
        self.var_lbl.setText(var_str)

        line_len_str = "" + "{:.2f}".format(line_len_str)
        self.line_len_lbl.setText(line_len_str)
        self.set_fs_band_lbls()

    def create_stat_select_time_rect(self, chn):
        """ Create the rectangle selector item.
        """
        redBrush = QBrush(QColor(217, 43, 24,50))
        self.statSelectTimeRect = pg.LinearRegionItem(
                        values=(self.edf_info.fs, 4 * self.edf_info.fs),
                        brush=redBrush, movable=True,
                        orientation=pg.LinearRegionItem.Vertical)
        self.statSelectTimeRect.setSpan((chn + 2) / (self.ci.nchns_to_plot + 3),
                                        (chn + 3) / (self.ci.nchns_to_plot + 3))
        self.main_plot.addItem(self.statSelectTimeRect)
        self.statSelectTimeRect.sigRegionChangeFinished.connect(self.stat_time_select_changed)
        self.stat_time_select_changed()

    def remove_stat_select_time_rect(self):
        """ Remove the rectangle selector item.
        """
        self.main_plot.removeItem(self.statSelectTimeRect)

    def stat_time_select_changed(self):
        """ Called when the stats bar is moved.
        """
        bounds = self.statSelectTimeRect.getRegion()
        bounds = (bounds[0] + self.count * self.edf_info.fs,
                    bounds[1] + self.count * self.edf_info.fs)
        mean_str, var_str, line_len_str = self.get_stats(int(bounds[0]), int(bounds[1]))
        mean_str = "" + "{:.2f}".format(mean_str)
        self.mean_sel_lbl.setText(mean_str)
        var_str = "" + "{:.2f}".format(var_str)
        self.var_sel_lbl.setText(var_str)
        line_len_str = "" + "{:.2f}".format(line_len_str)
        self.line_len_sel_lbl.setText(line_len_str)

        fs_band_dict = self.get_power_band_stats(int(bounds[0]), int(bounds[1]))
        for k in fs_band_dict.keys():
            key_str = "" + "{:.2e}".format(fs_band_dict[k])
            self.fs_band_sel_lbls[k].setText(key_str)

    def get_stats(self, s, f):
        """ Get mean, var, and line length.

        Args:
            chn: the channel to compute stats
            s: start time in samples
            f: end time in samples
        Returns:
            The mean
            var
            line length (for the part of the signal specified)
        """
        if self.filter_checked == 1:
            self.prep_filter_ws()
            array_sum = np.sum(self.filtered_data)
            mean_str = self.filtered_data[self.ssi.chn,s:f].mean()
            var_str = self.filtered_data[self.ssi.chn,s:f].var()
            line_len_str = np.sqrt(np.sum(np.diff(self.filtered_data[self.ssi.chn,s:f]) ** 2 + 1))
        else:
            mean_str = self.ci.data_to_plot[self.ssi.chn,s:f].mean()
            var_str = self.ci.data_to_plot[self.ssi.chn,s:f].var()
            line_len_str = np.sqrt(np.sum(np.diff(self.ci.data_to_plot[self.ssi.chn,s:f]) ** 2 + 1))

        return mean_str, var_str, line_len_str

    def get_power_band_stats(self, s, f):
        """ Get power band stats

        Args:
            chn: the channel to compute stats
            s: start time in samples
            f: end time in samples
        Returns:
            dict holding fs values (ex: {'alpha': #...})
        """
        data = self.ci.data_to_plot[self.ssi.chn,:]
        lp = 0
        hp = 0
        if self.filter_checked == 1:
            lp = self.fi.lp
            hp = self.fi.hp
        fs_band_dict = self.ssi.get_power(data, s, f, hp, lp, self.edf_info.fs)
        return fs_band_dict

    def set_fs_band_lbls(self):
        """ Sets alpha, beta, gamma, delta, theta lbls for stats.
        """
        fs_band_dict = self.get_power_band_stats(0, self.max_time * self.edf_info.fs)
        for k in fs_band_dict.keys():
            key_str = "" + "{:.2e}".format(fs_band_dict[k])
            self.fs_band_lbls[k].setText(key_str)

    def throw_alert(self, msg):
        """ Throws an alert to the user.
        """
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Information)
        alert.setText(msg)
        # alert.setInformativeText(msg)
        alert.setWindowTitle("Warning")
        alert.exec_()


class QHLine(QFrame):
    """ Class to create a horizontal line for UI """
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class PlotCanvas(FigureCanvas):
    """ Class to create a canvas to hold a matplotlib plot """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """ PlotCanvas constructor """
        self.fig = Figure(figsize=(width, height), dpi=dpi,
                          constrained_layout=False)
        self.gs = self.fig.add_gridspec(1, 1, wspace=0.0, hspace=0.0)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

def get_args():
    """ Function to setup arg parser.

        Args:
            --fn : name of the edf file (need to also use --montage-file)
            --predictions-file : name of the predictions file
            --montage-file : text file holding the montage
            --location : where in time to load the plot
            --export-png-file : path and filename to save the file as a png
            --window-width : how many second to show at once
            --filter : the filter arguments [filter_on, lp, hp, notch, bp1, bp2]
            --show : show the plot or exit immediately
            --print-annoations : show the annotations on the saved png
            --line-thickness : line thickness on the saved png
            --font-size : font size on the saved png
            --plot-title : title for the saved png
            --save-edf-fn : name and location to save the edf
            --anonymize-edf : anonymize fields in saved file or not
    """
    p = ap.ArgumentParser()

    # Add arguments
    p.add_argument("--fn", type=str,
                    help="Name of EDF file to load.")
    p.add_argument("--predictions-file", type=str, help="Name of prediction file.")
    p.add_argument("--montage-file", type=str, help="Text file with list of montage to load.")
    p.add_argument("--location", type=int, default=0,
                    help="Time in seconds to plot.")
    p.add_argument("--export-png-file", type=str,
                    help="Where to save image.")
    p.add_argument("--window-width", type=int, default=10,
                   choices=[5, 10, 15, 20, 25, 30],
                    help="The width of signals on the plot.")
    p.add_argument("--filter", nargs=6, type=float, default=[0,30,2,0,0,0],
                    help="1 or 0 to set the filter. Low pass, high pass, notch," +
                    "and bandpass frequencies. Set to 0 to turn off each filter.")
    p.add_argument("--show", type=int, default=1, choices=[0,1],
                    help="Whether or not to show the GUI.")
    p.add_argument("--print-annotations",type=int, default=1, choices=[0,1])
    p.add_argument("--line-thickness",type=float, default=0.5)
    p.add_argument("--font-size",type=int, default=12)
    p.add_argument("--plot-title", type=str, default="")
    p.add_argument("--save-edf-fn", type=str, default=None)
    p.add_argument("--anonymize-edf", type=int, default=1, choices=[0,1])
    p.add_argument("--prediction-thresh", type=float, default=0.5)

    return p.parse_args()

def check_args(args):
    """ Ensure that required arguments are present """
    mandatory_args = {'fn', 'montage_file', 'show'}
    if args.show == 0:
        if not mandatory_args.issubset(set(dir(args))):
            raise Exception(("You're missing essential arguments!"))

        if args.fn is None:
            raise Exception("--fn must be specified")
        if args.montage_file is None:
            raise Exception("--montage-file must be specified")

    if not args.fn is None and args.montage_file is None:
        raise Exception("--montage-file must be specified if --fn is specified")

    if args.fn is None and not args.montage_file is None:
        raise Exception("--fn must be specified if --montage-file is specified")

    if not args.fn is None:
        if not path.exists(args.fn):
            raise Exception("The --fn that you specifed does not exist.")

    if not args.montage_file is None:
        if not path.exists(args.montage_file):
            raise Exception("The --montage-file that you specifed does not exist.")
        elif not args.montage_file[len(args.montage_file) - 4:] == ".txt":
            raise Exception("The --montage-file must be a .txt file.")

    if not args.predictions_file is None:
        if not path.exists(args.predictions_file):
            raise Exception("The --predictions_file that you specifed does not exist.")
        elif not args.predictions_file[len(args.predictions_file) - 3:] == ".pt":
            raise Exception("The --predictions_file must be a .pt file.")
    
    if not (0 <= args.prediction_thresh <= 1):
        raise Exception("The --prediction-thresh must be between 0 and 1.")

    if not args.line_thickness is None:
        if args.line_thickness < 0.1 or args.line_thickness > 3:
            raise Exception("Please choose a line thickness between 0.1 and 3.")

    if not args.font_size is None:
        if args.font_size < 5 or args.line_thickness > 20:
            raise Exception("Please choose a font size between 5 and 20.")

    if not args.save_edf_fn is None:
        if not mandatory_args.issubset(set(dir(args))):
            raise Exception(("You're missing essential arguments!"))


if __name__ == '__main__':
    """ main, creates main plotting window """
    args = get_args()
    check_args(args)
    app = QApplication(sys.argv)
    ex = MainPage(args, app)
    sys.exit(app.exec_())
