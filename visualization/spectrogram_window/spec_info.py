""" Module for spec info data structure """
class SpecInfo():
    """ Data structure for holding information for spectrograms """

    def __init__(self):
        self.data = [] # data for plotting
        self.plot_spec = 0 # whether or not to plot spectrograms
        self.chn_plotted = -1 # channel to plot
        self.chn_name = "" # name of channel
        self.min_fs = 1 # min fs to plot
        self.max_fs = 30 # max fs to plot
