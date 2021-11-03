""" Module for the topoplot image saving """
import math
import numpy as np

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QHBoxLayout, QWidget, QCheckBox, QGridLayout,
                             QLineEdit, QDialogButtonBox, QFileDialog, QDoubleSpinBox,)
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

import mne

def _get_dim(num_plots):
    """ Get the dimensions of the subplot layout.

        Args:
            num_plots: the number of plots
        Returns:
            the number of rows and columns
    """
    num_r = math.floor(math.sqrt(num_plots))
    num_c = math.ceil(num_plots / num_r)
    return num_r, num_c

class SaveTopoplotOptions(QWidget):
    """ Class for the topoplot saving window """
    def __init__(self,parent):
        """ Constructor.

            Args:
                parent - the main (parent) window
        """
        super().__init__()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.width = int(parent.width / 2)
        self.height = int(parent.height / 2)
        self.left = int(centerPoint.x() - self.width / 2)
        self.top = int(centerPoint.y() - self.height / 2)
        self.title = 'Save topoplot'
        self.parent = parent
        self.plot_title = ""
        self.show_subplot_times = 0
        self.setup_ui()

    def setup_ui(self):
        """ Setup UI.
        """
        self.layout = QHBoxLayout()
        # left side - plot window
        self.m = PlotCanvas(self, width=7, height=7)
        self.layout.addWidget(self.m)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(QSize(self.width, self.height))

        # right side - options
        self.rt_side_layout = QGridLayout()
        self.cbox_add_times = QCheckBox("Add times to subplots", self)
        self.cbox_title = QCheckBox("Show title:", self)
        self.cbox_single_time = QCheckBox("Single plot (time in sec):", self)
        self.title_input = QLineEdit(self)
        self.spinbox_single_time = QDoubleSpinBox(self)
        line_val = self.parent.topoplot_line.value() + self.parent.count * self.parent.edf_info.fs
        line_val = line_val / self.parent.edf_info.fs
        self.plot_single_time = 0 # default to plotting everything
        self.plot_at_time = self._get_pred_sample_from_time(line_val) # start where line is
        print(self.plot_at_time)
        self.spinbox_single_time.setRange(0, self.parent.max_time - 1)
        self.spinbox_single_time.setValue(line_val)
        self.rt_side_layout.addWidget(self.cbox_single_time, 0,0,1,1)
        self.rt_side_layout.addWidget(self.spinbox_single_time, 0,1,1,1)
        self.rt_side_layout.addWidget(self.cbox_add_times, 1,0,1, 2)
        self.rt_side_layout.addWidget(self.cbox_title, 2,0,1,1)
        self.rt_side_layout.addWidget(self.title_input, 2,1,1,1)
        self.ok_btn = QtWidgets.QDialogButtonBox(self)
        self.ok_btn.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.rt_side_layout.addWidget(self.ok_btn,3,1,1,1)
        self.layout.addLayout(self.rt_side_layout)

        self.setLayout(self.layout)
        self.set_sig_slots()

    def set_sig_slots(self):
        """ Set signals and slots
        """
        self.ok_btn.button(QDialogButtonBox.Ok).clicked.connect(self.print_plot)
        self.ok_btn.button(QDialogButtonBox.Cancel).clicked.connect(self.close_window)
        self.cbox_add_times.toggled.connect(self.add_times)
        self.cbox_title.toggled.connect(self.title_checked)
        self.cbox_single_time.toggled.connect(self.toggle_plot_single_time)
        self.spinbox_single_time.valueChanged.connect(self.change_single_time)
        self.title_input.textChanged.connect(self.title_changed)
        self.make_plot()
        self.show()

    def add_times(self):
        """ Called when cbox is checked to set the times on the plot.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.show_subplot_times = 1
        else:
            self.show_subplot_times = 0
        self.make_plot()

    def title_checked(self):
        """ Set or change the title on the plot.
        """
        if self.cbox_title.isChecked():
            self.plot_title = self.title_input.text()
        else:
            self.plot_title = ""
        self.m.fig.suptitle(self.plot_title)
        self.m.draw()

    def title_changed(self):
        """ Call title_checked to update the title.
        """
        self.title_checked()

    def toggle_plot_single_time(self):
        """ Called when the single plot button is checked.
        """
        if self.cbox_single_time.isChecked():
            self.plot_single_time = 1
        else:
            self.plot_single_time = 0
        self.plot_at_time = self._get_pred_sample_from_time(self.spinbox_single_time.value())
        self.make_plot()

    def change_single_time(self):
        """ Call toggle_plot_single_time to update the time of the plot.
        """
        self.toggle_plot_single_time()

    def _get_pred_sample_from_time(self, time_val:float):
        """ Get the value of the prediction from the time.

            Args:
                time_val: the value of the spinbox in time
            Returns:
                The value converted to the location in preds
        """
        val_samples = time_val * self.parent.edf_info.fs
        pred_loc = int(val_samples / self.parent.pi.pred_width)
        return pred_loc

    def make_plot(self):
        """ Plot the topoplots.
        """
        self.m.fig.clf()
        num_plots, start = self._get_num_subplots()
        self.ax = []
        dim_r, dim_c = _get_dim(num_plots)
        for i in range(num_plots):
            self.ax.append(self.m.fig.add_subplot(dim_r, dim_c, i + 1))

            # make mne plot
            curr_score = self.parent.pi.preds_to_plot[start + i,:]
            # Create the layout
            layout = mne.channels.read_layout('EEG1005')
            pos2d = []
            layout_names = [name.upper() for name in layout.names]
            for ch in reversed(self.parent.ci.labels_to_plot):
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

            _, _ = mne.viz.plot_topomap(curr_score, pos2d, sphere=1,
                                  axes=self.ax[i], vmin=0, vmax=1, show=False,
                                  outlines='head')

            if self.show_subplot_times:
                title = self._get_time(start, i)
                self.ax[i].set_title(str(title) + "s")
            self.m.fig.suptitle(self.plot_title)
        self.m.draw()

    def _get_num_subplots(self):
        """ Compute the number of subplots needed.

            Returns:
                The number of predictions in the window and
                the start location as an index.
        """
        if self.plot_single_time:
            num_plots = 1
            start = self.plot_at_time
            return num_plots, start
        count = self.parent.count
        ws = self.parent.window_size
        width = int(self.parent.pi.pred_width)
        fs = self.parent.edf_info.fs
        for i in range(count* fs,(count + ws) * fs):
            if i % width == 0:
                start = i / width
                break

        for i in range((count + ws) * fs - width, (count + ws) * fs):
            if i % width == 0:
                end = i / width
                break

        num_plots = int(end - start) + 1
        return num_plots, int(start)

    def _get_time(self, start, i):
        """ Returns the time in seconds.

            Args:
                start: the start index in predictions
                i: the current index in predictions
            Returns:
                The time in seconds.
        """
        samples = (start + i) * self.parent.pi.pred_width
        samples = samples / self.parent.edf_info.fs
        return samples

    def print_plot(self):
        """ Saves the plot and exits.
        """
        file = QFileDialog.getSaveFileName(self, 'Save File')
        if len(file[0]) == 0 or file[0] is None:
            return
        self.m.fig.savefig(file[0] + ".png", bbox_inches='tight', dpi=300)
        self.close_window()

    def close_window(self):
        """ Called when "ok" is pressed to exit.
        """
        self.parent.savetopo_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.savetopo_win_open = 0
        event.accept()

class PlotCanvas(FigureCanvas):
    """ Class for the matplotlib graph as a widget """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """ Constructor """
        self.fig = Figure(figsize=(width, height), dpi=dpi,
                          constrained_layout=False)
        self.gs = self.fig.add_gridspec(1, 1, wspace=0.0, hspace=0.0)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
