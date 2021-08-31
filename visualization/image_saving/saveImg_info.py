""" Module to hold info needed for print preview """
class SaveImgInfo():
    """ Data structure for holding information for print preview
        and saving images """

    def __init__(self):
        """ Constructor.

            Parameters:
                Parameters to edit:
                    plotAnn - whether to plot annotations
                    linethick - the line thickness
                    fontsize - the font size
                    plottitle - whether or not to plot a title
                    title - the text of the title
                Parameters needed to plot from parent:
                    data - the data for plotting
                    pi - the preds info object
                    ci - the channel info object
                    predicted - self.predicted from parent
                    fs - the fs
                    count - the current location of the graph
                    window_size - width of the window
                    y_lim - the amplitude for plotting
                    thresh - the threshold for predictions
        """
        # Parameters to edit
        self.plot_ann = 1
        self.line_thick = 0.5
        self.font_size = 12
        self.plot_title = 0
        self.title = ""
        # Parameters for plotting from parent
        self.data = []
        self.pi = []
        self.ci = []
        self.predicted = 0
        self.fs = 0
        self.count = 0
        self.window_size = 10
        self.y_lim = 150
        self.thresh = 0.5
