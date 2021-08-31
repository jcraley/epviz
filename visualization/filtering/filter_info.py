""" Module to hold information for filtering. """
class FilterInfo():
    """ Data structure for holding information for filtering. """

    def __init__(self):
        """ Constructor of the filter info object.

            Variables:
                fs - the fs of the signal
                hp - the hp fs of the filter
                lp - the lp fs of the filter
                notch - the notch fs of the filter
                bp1 - the low bandpass fs of the filter
                bp2 - the high bandpass fs of the filter
                do_lp - whether to lowpass filter or not
                do_hp - whether to high pass filter or not
                do_notch - whether to notch filter or not
                do_bp - whether to bandpass filter or not
                filter_canceled - used to determine if filtering
                    was canceled during edf saving
        """
        self.fs = 0
        self.hp = 2
        self.lp = 30
        self.notch = 60
        self.bp1 = 0
        self.bp2 = 0
        self.do_lp = 1
        self.do_hp = 1
        self.do_notch = 0
        self.do_bp = 0
        self.filter_canceled = 0
