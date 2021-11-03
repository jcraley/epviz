""" Module for saving to an image """
import sys
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QFileDialog

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from visualization.plot_utils import check_annotations
from visualization.ui_files.saveImg import Ui_Form

class SaveImgOptions(QWidget):
    """ Class for the print preview window """
    def __init__(self,data,parent):
        """ Constructor.

            Args:
                data - the save image info object
                parent - the main (parent) window
        """
        super().__init__()
        self.data = data
        self.parent = parent
        self.sio_ui = Ui_Form()
        self.sio_ui.setupUi(self)
        self.setup_ui() # Show the GUI

    def setup_ui(self):
        """ Setup the UI for the window.
        """
        self.m = PlotCanvas(self, width=7, height=7)
        self.sio_ui.plot_layout.addWidget(self.m)

        self.set_sig_slots()

    def set_sig_slots(self):
        """ Set signals and slots
        """
        self.sio_ui.okBtn.button(QDialogButtonBox.Ok).clicked.connect(self.print_plot)
        self.sio_ui.okBtn.button(QDialogButtonBox.Cancel).clicked.connect(self.close_window)

        self.ann_list = []
        self.aspan_list = []

        self.nchns = self.data.ci.nchns_to_plot
        self.fs = self.data.fs
        self.plot_data = self.data.data
        self.count = self.data.count
        self.window_size = self.data.window_size
        self.y_lim = self.data.y_lim
        self.predicted = self.data.predicted
        self.thresh = self.data.thresh

        # add items to the combo boxes
        self.sio_ui.textSizeInput.addItems(["6pt","8pt","10pt", "12pt",
                                            "14pt", "16pt"])
        self.sio_ui.textSizeInput.setCurrentIndex(3)

        self.sio_ui.lineThickInput.addItems(["0.25px","0.5px","0.75px",
                                             "1px","1.25px","1.5px","1.75px",
                                             "2px"])
        self.sio_ui.lineThickInput.setCurrentIndex(1)

        self.sio_ui.annCbox.setChecked(1)

        self.make_plot()

        if (not self.parent.argv.export_png_file is None) and self.parent.init == 0:
            self.data.plot_ann = self.parent.argv.print_annotations
            self.data.line_thick = self.parent.argv.line_thickness
            self.data.font_size = self.parent.argv.font_size
            self.data.plot_title = 1
            self.data.title = self.parent.argv.plot_title
            self.make_plot()
            self.print_plot()
        else:
            self.show()

    def ann_checked(self):
        """ Called when the annotation cbox is toggled.
        """
        cbox = self.sender()
        if cbox.isChecked():
            self.data.plot_ann = 1
        else:
            self.data.plot_ann = 0
        self.make_plot()

    def title_checked(self):
        """ Called when the title cbox is toggled.
        """
        if self.sio_ui.titleCbox.isChecked():
            self.data.title = self.sio_ui.titleInput.text()
        else:
            self.data.title = ""
        self.ax.set_title(self.data.title, fontsize=self.data.font_size)
        self.m.draw()

    def title_changed(self):
        """ Called when the text in the title input is changed.
        """
        self.title_checked()

    def chg_line_thick(self):
        """ Called when the line thickness is changed.
        """
        thickness = self.sio_ui.lineThickInput.currentText()
        thickness = float(thickness.split("px")[0])
        self.data.line_thick = thickness
        self.make_plot()

    def chg_text_size(self):
        """ Called when the font size is changed.
        """
        font_size = self.sio_ui.textSizeInput.currentText()
        font_size = int(font_size.split("pt")[0])
        self.data.font_size = font_size
        self.make_plot()

    def make_plot(self):
        """ Makes the plot with the given specifications.
        """
        self.m.fig.clf()
        self.ax = self.m.fig.add_subplot(self.m.gs[0])

        del self.ax.lines[:]
        for i, a in enumerate(self.ann_list):
            a.remove()
        self.ann_list[:] = []
        for aspan in self.aspan_list:
            aspan.remove()
        self.aspan_list[:] = []

        for i in range(self.nchns):
            if self.data.plot_ann:
                self.ax.plot(self.plot_data[i, :]
                             + (i + 1) * self.y_lim, '-', linewidth=self.data.line_thick,
                             color=self.data.ci.colors[i])
                self.ax.set_ylim([-self.y_lim, self.y_lim * (self.nchns + 1)])
                self.ax.set_yticks(np.arange(0, (self.nchns + 1)*self.y_lim, step=self.y_lim))
                self.ax.set_yticklabels(self.data.ci.labels_to_plot, fontdict=None,
                                        minor=False, fontsize=self.data.font_size)
                width = 1 / (self.nchns + 2)
            else:
                self.ax.plot(self.plot_data[i, :] + (i) * self.y_lim,
                            '-', linewidth=self.data.line_thick,
                            color=self.data.ci.colors[i])
                self.ax.set_ylim([-self.y_lim, self.y_lim * (self.nchns)])
                self.ax.set_yticks(np.arange(0, (self.nchns)*self.y_lim, step=self.y_lim))
                self.ax.set_yticklabels(self.data.ci.labels_to_plot[1:], fontdict=None,
                                        minor=False, fontsize=self.data.font_size)
                width = 1 / (self.nchns + 1)

            if self.predicted == 1:
                starts, ends, chns, class_vals = self.data.pi.compute_starts_ends_chns(self.thresh,
                                            self.count, self.window_size, self.fs, self.nchns)
                for k in range(len(starts)):
                    if self.data.pi.pred_by_chn and not self.data.pi.multi_class:
                        if chns[k][i]:
                            if i == self.plot_data.shape[0] - 1:
                                if self.data.plot_ann:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+1.5),
                                                            ymax=1, color='paleturquoise',
                                                            alpha=1))
                                else:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+0.5),
                                                            ymax=1, color='paleturquoise',
                                                            alpha=1))
                            else:
                                if self.data.plot_ann:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count * self.fs,
                                                            ymin=width*(i+1.5), ymax=width*(i+2.5),
                                                            color='paleturquoise', alpha=1))
                                else:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+0.5),
                                                            ymax=width*(i+1.5),
                                                            color='paleturquoise',
                                                            alpha=1))
                            x_vals = range(int(starts[k]) - self.count * self.fs,
                                            int(ends[k]) - self.count * self.fs)
                            if self.data.plot_ann:
                                self.ax.plot(x_vals, self.plot_data[i, int(starts[k])
                                            - self.count * self.fs:int(ends[k])
                                            - self.count * self.fs] + i * self.y_lim
                                            + self.y_lim, '-',
                                            linewidth=self.data.line_thick * 2,
                                            color=self.data.ci.colors[i])
                            else:
                                self.ax.plot(x_vals, self.plot_data[i, int(starts[k])
                                            - self.count * self.fs:int(ends[k])
                                            - self.count * self.fs] + (i - 1) * self.y_lim
                                            + self.y_lim, '-',
                                            linewidth=self.data.line_thick * 2,
                                            color=self.data.ci.colors[i])
                    elif not self.data.pi.pred_by_chn and not self.data.pi.multi_class:
                        self.aspan_list.append(self.ax.axvspan(starts[k] - self.count * self.fs,
                                ends[k] - self.count * self.fs, color='paleturquoise', alpha=0.5))
                    elif not self.data.pi.pred_by_chn and self.data.pi.multi_class:
                        if i == 0: # only plot for first chn
                            r, g, b, a = self.data.pi.get_color(class_vals[k])
                            r = r / 255
                            g = g / 255
                            b = b / 255
                            a = a / 255
                            self.aspan_list.append(self.ax.axvspan(starts[k] - self.count * self.fs,
                                    ends[k] - self.count * self.fs, color=(r,g,b,a)))
                    else:
                        for i in range(self.nchns):
                            r, g, b, a = self.data.pi.get_color(chns[i][k])
                            r = r / 255
                            g = g / 255
                            b = b / 255
                            a = a / 255
                            if i == self.plot_data.shape[0] - 1:
                                if self.data.plot_ann:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+1.5),
                                                            ymax=1, color=(r,g,b,a)))
                                else:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+0.5),
                                                            ymax=1, color=(r,g,b,a)))
                            else:
                                if self.data.plot_ann:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count * self.fs,
                                                            ymin=width*(i+1.5), ymax=width*(i+2.5),
                                                            color=(r,g,b,a)))
                                else:
                                    self.aspan_list.append(self.ax.axvspan(starts[k] -
                                                            self.count * self.fs,
                                                            ends[k] - self.count *
                                                            self.fs, ymin=width*(i+0.5),
                                                            ymax=width*(i+1.5),
                                                            color=(r,g,b,a)))


        self.ax.set_xlim([0, self.fs*self.window_size])
        step_size = self.fs  # Updating the x labels with scaling
        step_width = 1
        if self.window_size >= 15 and self.window_size <= 25:
            step_size = step_size * 2
            step_width = step_width * 2
        elif self.window_size > 25:
            step_size = step_size * 3
            step_width = step_width * 3
        self.ax.set_xticks(np.arange(0, self.window_size *
                                     self.fs + 1, step=step_size))
        self.ax.set_xticklabels(np.arange(self.count, self.count + self.window_size + 1,
                                          step=step_width), fontdict=None,
                                          minor=False, fontsize=self.data.font_size)
        self.ax.set_xlabel("Time (s)", fontsize=self.data.font_size)
        self.ax.set_title(self.data.title, fontsize=self.data.font_size)

        if self.data.plot_ann:
            ann, idx_w_ann = check_annotations(
                self.count, self.window_size, self.parent.edf_info)
            font_size = self.data.font_size - 4
            # Add in annotations
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
                            self.ann_list.append(self.ax.annotate(txt, xy=(
                                (int_prev - self.count)*self.fs, -self.y_lim / 2 + self.y_lim),
                                color='black', size=font_size))
                        else:
                            self.ann_list.append(self.ax.annotate(txt, xy=(
                                (int_prev - self.count)*self.fs, -self.y_lim / 2),
                                color='black', size=font_size))
                        txt = ann[2, i]
                    int_prev = int_i
                if txt != "":
                    if idx_w_ann[int_i - self.count] and int_i % 2 == 1:
                        self.ann_list.append(self.ax.annotate(txt, xy=(
                            (int_i - self.count)*self.fs, -self.y_lim / 2 + self.y_lim),
                            color='black', size=font_size))
                    else:
                        self.ann_list.append(self.ax.annotate(
                            txt, xy=((int_i - self.count)*self.fs, -self.y_lim / 2),
                            color='black', size=font_size))

        self.m.draw()

    def print_plot(self):
        """ Saves the plot and exits.
        """
        if (not self.parent.argv.export_png_file is None) and self.parent.init == 0:
            self.ax.figure.savefig(self.parent.argv.export_png_file,
                                    bbox_inches='tight', dpi=300)
            if self.parent.argv.show == 0:
                sys.exit()
            else:
                self.close_window()
        else:
            file = QFileDialog.getSaveFileName(self, 'Save File')
            if len(file[0]) == 0 or file[0] is None:
                return
            else:
                self.ax.figure.savefig(file[0] + ".png",
                                bbox_inches='tight', dpi=300)
                self.close_window()

    def reset_initial_state(self):
        """ Reset initial values for the next time this window is opened.
        """
        self.data.plot_ann = 1
        self.data.line_thick = 0.5
        self.data.font_size = 12
        self.data.plot_title = 0
        self.data.title = ""

    def close_window(self):
        """ Close the window and exit.
        """
        self.parent.saveimg_win_open = 0
        self.reset_initial_state()
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.saveimg_win_open = 0
        self.reset_initial_state()
        event.accept()

class PlotCanvas(FigureCanvas):
    """ Plot canvas class used to make a matplotlib graph into a widget.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """ Create the widget.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi,
                          constrained_layout=False)
        self.gs = self.fig.add_gridspec(1, 1, wspace=0.0, hspace=0.0)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
