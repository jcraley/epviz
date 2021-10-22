""" Module for the organize channels window """
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QWidget, QListWidget, QPushButton, QLabel,
                                QGridLayout, QScrollArea, QListWidgetItem,
                                QAbstractItemView)

import numpy as np
from signal_loading.channel_info import ChannelInfo

from matplotlib.backends.qt_compat import QtWidgets


class OrganizeChannels(QWidget):
    """ Class for the organize channels window """
    def __init__(self,data,parent):
        """ Constructor for organize channels.

            Args:
                data - the channel info object
                parent - the main (parent) window
        """
        super().__init__()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        print(centerPoint)
        self.width = int(parent.width / 6)
        self.height = int(parent.height / 2.5)
        self.left = centerPoint.x() - self.width / 2
        self.top = centerPoint.y() - self.height / 2
        self.title = 'Organize signals'
        self.data = data
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """ Setup UI for the organize channels window.
        """
        grid_lt = QGridLayout()

        self.scroll = QScrollArea()
        self.scroll.setMinimumWidth(120)
        self.scroll.setMinimumHeight(200)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.chn_qlist = QListWidget()
        self.chn_qlist.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chn_qlist.setDragEnabled(True)
        self.chn_qlist.setDragDropMode(QAbstractItemView.InternalMove)
        self.chn_qlist.setDropIndicatorShown(True)

        self.scroll.setWidget(self.chn_qlist)
        self.populateChnList()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(QSize(self.width, self.height))

        lbl_info = QLabel("Drag and drop channels \n to change their order: ")
        grid_lt.addWidget(lbl_info,0,0)

        btn_exit = QPushButton('Ok', self)
        btn_exit.clicked.connect(self.updateChnOrder)
        grid_lt.addWidget(btn_exit,2,0)
        grid_lt.addWidget(self.scroll,1,0)
        self.setLayout(grid_lt)

        self.show()

    def populateChnList(self):
        """ Fills the list with all of the channels to be loaded.
        """
        self.chn_items = []
        self.labels_flipped = []
        self.data.organize = 1 # set that channels were organized
        if len(self.data.labels_to_plot) == 0:
            self.close_window()
        else:
            for i in range(len(self.data.labels_to_plot) - 1):                
                self.labels_flipped.append(self.data.labels_to_plot[i+1])
                self.chn_items.append(QListWidgetItem(self.data.labels_to_plot[len(self.data.labels_to_plot) - 1 - i], self.chn_qlist))
                self.chn_qlist.addItem(self.chn_items[i])
            self.scroll.show()

    def updateChnOrder(self):
        """ Function to check the clicked channels and exit.
        """
        temp_labels = ["Notes"]
        temp_colors = []
        temp_data = np.zeros(self.data.data_to_plot.shape)
        for i in range(len(self.data.colors)):
            temp_labels.append(self.data.labels_to_plot[i+1])
            temp_colors.append(self.data.colors[i])
            temp_data[i,:] += self.data.data_to_plot[i,:]

        for k in range(len(self.chn_items)):
            row = self.chn_qlist.row(self.chn_items[k])
            temp_labels[len(self.chn_items) - row] = self.chn_items[k].text()
            temp_colors[len(self.chn_items) - row - 1] = self.data.colors[len(self.chn_items) - k - 1]
            temp_data[len(self.chn_items) - row - 1,:] = self.data.data_to_plot[len(self.chn_items) - k - 1,:]
        self.data.labels_to_plot = temp_labels
        self.data.colors = temp_colors
        self.data.data_to_plot = temp_data
        self.parent.call_initial_move_plot()
        self.close_window()

    def close_window(self):
        """ Closes the window.
        """
        self.parent.organize_win_open = 0
        self.close()

    def closeEvent(self, event):
        """ Called when the window is closed.
        """
        self.parent.organize_win_open = 0
        event.accept()
