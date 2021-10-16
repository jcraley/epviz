""" Module for prediction options window """
from PyQt5.QtWidgets import (QFileDialog, QWidget, QPushButton, QCheckBox,
                                QLabel, QGridLayout, QFrame, QRadioButton,
                                QGroupBox, QHBoxLayout)

from matplotlib.backends.qt_compat import QtWidgets

class PredictionOptions(QWidget):
    """ Class for prediction options window """
    def __init__(self,pi,parent):
        """ Constructor """
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Prediction Options'
        self.width = int(parent.width / 3)
        self.height = int(parent.height / 3)
        self.data = pi
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """ Setup window UI
        """
        layout = QGridLayout()
        layout.setSpacing(4)

        self.setWindowTitle(self.title)
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.setGeometry(center_point.x() - int(self.width / 2),
            center_point.y() - int(self.height / 2), self.width, self.height)

        info_lbl = QLabel(self)
        info_lbl.setText("Loading predictions:" +
                        "\n" +
                        "\n - Must be pytorch (.pt) files" +
                        "\n - Can load either predictions OR preprocessed data and a model" +
                        "\n - Output is expected to be of length (k * number of samples in" +
                        " the edf file) = c" +
                        "\n    where k and c are integers"
                        "\n - Output will be assumed to be for non-overlapping intervals" +
                        " of constant width" +
                        "\n - Channel-wise predictions will be plotted starting from the" +
                        " top of the screen" +
                        "\n - Predictions are assumed to be binary" +
                        "\n - To use multi-class predictions, select 'multi-class'" +
                        "\n - For multi-class predictions, output must be size" +
                        "\n   (num predictions, <chns, optional>, num classes)")
        layout.addWidget(info_lbl, 0, 0, 1, 4)

        layout.addWidget(QLabel(), 1, 0, 1, 4)

        layout.addWidget(QHLine(), 2, 0, 1, 4)

        layout.addWidget(QLabel(), 3, 0, 1, 4)
        ud = 4


        self.cbox_preds = QCheckBox("Plot predictions from file",self)

        self.cbox_model = QCheckBox("Plot model predictions",self)
        self.cbox_model.toggled.connect(self.model_checked)
        self.cbox_model.setToolTip("Click to plot model predictions")
        if self.data.plot_model_preds == 1:
            self.cbox_model.setChecked(True)
        elif self.data.plot_model_preds == 1:
            self.cbox_model.setChecked(False)
            self.data.plot_model_preds = 0

        layout.addWidget(self.cbox_model,ud,0)

        button_load_pt_file = QPushButton("Load preprocessed data",self)
        button_load_pt_file.clicked.connect(self.load_pt_data)
        button_load_pt_file.setToolTip("Click to load preprocessed data (as a torch tensor)")
        layout.addWidget(button_load_pt_file,ud,1)

        self.label_load_pt_file = QLabel("No data loaded.",self)
        if self.data.data_loaded == 1:
            self.label_load_pt_file.setText(self.data.data_fn)
        layout.addWidget(self.label_load_pt_file,ud,2)
        groupbox_binary_edit_model = QGroupBox()
        self.radio_binary_model = QRadioButton("binary")
        self.radio_multiclass_model = QRadioButton("multi-class")
        if self.data.multi_class_model:
            self.radio_multiclass_model.setChecked(True)
        else:
            self.radio_binary_model.setChecked(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.radio_binary_model)
        hbox.addWidget(self.radio_multiclass_model)
        groupbox_binary_edit_model.setLayout(hbox)
        layout.addWidget(groupbox_binary_edit_model, ud, 3)
        ud += 1
        layout.addWidget(QLabel(), ud, 0, 1, 4)
        ud += 1

        button_load_model = QPushButton("Load model",self)
        button_load_model.clicked.connect(self.load_model)
        button_load_model.setToolTip("Click to load model")
        layout.addWidget(button_load_model,ud,1)

        self.label_load_model = QLabel("No model loaded.",self)
        if self.data.model_loaded == 1:
            self.label_load_model.setText(self.data.model_fn)
        layout.addWidget(self.label_load_model,ud,2)
        ud += 1
        layout.addWidget(QLabel(), ud, 0, 1, 4)
        ud += 1

        self.cbox_preds.toggled.connect(self.preds_checked)
        self.cbox_preds.setToolTip("Click to plot predictions from file")
        if self.data.plot_loaded_preds == 1:
            self.cbox_preds.setChecked(True)
        elif self.data.plot_loaded_preds == 1:
            self.cbox_preds.setChecked(False)
            self.data.plot_loaded_preds = 0

        layout.addWidget(self.cbox_preds,ud,0)

        button_load_preds = QPushButton("Load predictions",self)
        button_load_preds.clicked.connect(self.load_preds)
        button_load_preds.setToolTip("Click to load predictions")
        layout.addWidget(button_load_preds,ud,1)

        self.label_load_preds = QLabel("No predictions loaded.", self)
        if self.data.preds_loaded == 1:
            self.label_load_preds .setText(self.data.preds_fn)
        layout.addWidget(self.label_load_preds ,ud,2)

        groupbox_binary_edit_preds = QGroupBox()
        self.radio_binary_preds = QRadioButton("binary")
        self.radio_multiclass_preds = QRadioButton("multi-class")
        if self.data.multi_class_preds:
            self.radio_multiclass_preds.setChecked(True)
        else:
            self.radio_binary_preds.setChecked(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.radio_binary_preds)
        hbox.addWidget(self.radio_multiclass_preds)
        groupbox_binary_edit_preds.setLayout(hbox)
        layout.addWidget(groupbox_binary_edit_preds, ud, 3)

        ud += 1

        btn_exit = QPushButton('Ok', self)
        btn_exit.clicked.connect(self.check)
        layout.addWidget(btn_exit,ud,4)

        self.setLayout(layout)

        self.show()

    def model_checked(self):
        """ Called when the model cbox is checked.
        """
        cbox = self.sender()
        if cbox.isChecked():
            if self.cbox_preds.isChecked():
                self.cbox_preds.setChecked(False)

    def preds_checked(self):
        """ Called when the predictions cbox is checked.
        """
        cbox = self.sender()
        if cbox.isChecked():
            if self.cbox_model.isChecked():
                self.cbox_model.setChecked(False)

    def load_pt_data(self):
        """ Load data for prediction.
        """
        ptfile_fn = QFileDialog.getOpenFileName(self, 'Open file','.','Pytorch files (*.pt)')
        if ptfile_fn[0] is None or len(ptfile_fn[0]) == 0:
            return
        if len(ptfile_fn[0].split('/')[-1]) < 18:
            self.data.data_fn = ptfile_fn[0].split('/')[-1]
        else:
            self.data.data_fn = ptfile_fn[0].split('/')[-1][0:15] + "..."
        self.label_load_pt_file.setText(self.data.data_fn)
        self.data.set_data(ptfile_fn[0])
        self.cbox_model.setChecked(True)
        self.cbox_preds.setChecked(False)

    def load_model(self):
        """ Load model for prediction
        """
        model_fn = QFileDialog.getOpenFileName(self, 'Open model','.','Pytorch files (*.pt)')
        if model_fn[0] is None or len(model_fn[0]) == 0:
            return
        if len(model_fn[0].split('/')[-1]) < 18:
            self.data.model_fn = model_fn[0].split('/')[-1]
        else:
            self.data.model_fn = model_fn[0].split('/')[-1][0:15] + "..."
        self.label_load_model.setText(self.data.model_fn)
        self.data.set_model(model_fn[0])
        self.cbox_model.setChecked(True)
        self.cbox_preds.setChecked(False)

    def load_preds(self):
        """ Loads predictions
        """
        preds_fn = QFileDialog.getOpenFileName(self, 'Open predictions','.','Pytorch files (*.pt)')
        if preds_fn[0] is None or len(preds_fn[0]) == 0:
            return
        if (self.data.set_preds(preds_fn[0], self.parent.max_time,
            self.parent.edf_info.fs, self.parent.ci.nchns_to_plot,
            self.radio_binary_preds.isChecked()) == -1):
            self.parent.throw_alert("Predictions are not an even multiple of the" +
                            " samples in the .edf" +
                            "file you loaded or are the incorrect shape." +
                            " Please check your file.")
        else:
            if len(preds_fn[0].split('/')[-1]) < 18:
                self.data.preds_fn = preds_fn[0].split('/')[-1]
            else:
                self.data.preds_fn = preds_fn[0].split('/')[-1][0:15] + "..."
            self.label_load_preds.setText(self.data.preds_fn)
            self.cbox_model.setChecked(False)
            self.cbox_preds.setChecked(True)

    def check(self):
        """ Take loaded model and data and compute predictions
        """
        nchns = self.parent.ci.nchns_to_plot
        # reset topoplot
        self.parent.btn_topo.setEnabled(0)
        self.parent.btn_topo.setText("Show topoplots")
        self.parent.topoplot_dock.hide()
        # if nothing is checked, then turn off predictions
        if not self.cbox_model.isChecked() and not self.cbox_preds.isChecked():
            self.parent.predicted = 0
            self.close_window()
            self.parent.call_move_plot(0, 0, 0)
        elif self.cbox_preds.isChecked():
            if not self.data.preds_loaded:
                self.parent.throw_alert("Please load predictions.")
            else:
                loaded_preds_valid = self.data.check_preds_shape(self.data.preds, 0,
                                        self.parent.max_time, self.parent.edf_info.fs,
                                        nchns, self.radio_binary_preds.isChecked())
                if not loaded_preds_valid:
                    self.parent.predicted = 1
                    self.data.preds_to_plot = self.data.preds
                    self.data.multi_class_preds = self.data.multi_class
                    self.parent.pred_label.setText("Predictions plotted.")
                    topo_chns_correct = self.parent.check_topo_chns()
                    if (self.data.pred_by_chn and not self.data.multi_class
                        and topo_chns_correct):
                        self.parent.add_topoplot()
                        self.parent.btn_topo.setEnabled(1)
                        self.parent.btn_topo.setText("Hide topoplots")
                    self.parent.call_move_plot(0,0,0)
                    self.close_window()
                elif loaded_preds_valid == -1:
                    self.parent.throw_alert("Predictions are not an even multiple" +
                                    " of the samples in the .edf" +
                                    "file you loaded or are the incorrect shape." +
                                    " Please check your file.")
        else:
            if self.data.ready:
                preds_ret = self.data.predict(self.parent.max_time,
                                self.parent.edf_info.fs,nchns,
                                self.radio_binary_model.isChecked())
                if preds_ret == -2:
                    self.parent.throw_alert("An error occured when trying to call the predict() " +
                                "function using your model. Please check your model and data.")
                elif preds_ret == -1:
                    self.parent.throw_alert("Predictions are not an even multiple" +
                                    " of the samples in the .edf" +
                                    "file you loaded or are the incorrect shape." +
                                    " Please check your file.")
                else:
                    self.parent.predicted = 1
                    self.data.preds_to_plot = self.data.model_preds
                    self.data.multi_class_model = self.data.multi_class
                    self.parent.pred_label.setText("Predictions plotted.")
                    topo_chns_correct = self.parent.check_topo_chns()
                    if (self.data.pred_by_chn and not self.data.multi_class
                        and topo_chns_correct):
                        self.parent.add_topoplot()
                        self.parent.btn_topo.setEnabled(1)
                        self.parent.btn_topo.setText("Hide topoplots")
                    self.parent.call_move_plot(0,0,0)
                    self.close_window()
            elif not self.data.data_loaded:
                self.parent.throw_alert('Please load data.')
            else:
                self.parent.throw_alert('Please load a model.')

    def close_window(self):
        """ Called to close the predictions window.

            For when zoom plot is open, if new predictions are
            loaded they will make the roi box invisible
        """
        if self.parent.btn_zoom.text() == "Close zoom":
            self.parent.open_zoom_plot()
            self.parent.open_zoom_plot()
        self.parent.close_topoplot()
        topo_chns_correct = self.parent.check_topo_chns()
        if (self.parent.pi.pred_by_chn and self.parent.predicted
                and topo_chns_correct and not self.parent.pi.multi_class):
            self.parent.add_topoplot()
            self.parent.btn_topo.setText("Hide topoplots")
            self.parent.btn_topo.setEnabled(1)
        self.parent.preds_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.preds_win_open = 0
        event.accept()

class QHLine(QFrame):
    """ Class for horizontal line widget """
    def __init__(self):
        """ Constructor """
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
