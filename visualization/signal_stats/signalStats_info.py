""" Module to compute power statistics for the signals """
from copy import deepcopy
import numpy as np

class SignalStatsInfo():
    """ Class to hold relevant information for computing statistics
    """
    def __init__(self):
        """ Constructor.
            fs_bands - holds dict of bands, can be expanded
            chn - the channel that we are getting power for
            chn_items - channel info in the stats window in parent
        """
        self.chn = 0
        self.chn_items = []
        self.fs_bands = {'delta':(1,4),
                         'theta':(4,8),
                         'alpha':(8,14),
                         'beta':(14,30),
                         'gamma': (30,45)}

    def _get_power_for_band(self, sig, s, f, band, l, h, fs):
        """ Returns the power in the given fs band.

        Args:
            sig: the signal to use
            s: where to start in samples
            f: where to end in samples
            band: which type of band ('delta','theta','alpha','beta','gamma')
            l: low pass fs of filter
            h: high pass fs of filter
            fs: the fs of the signal
        Returns:
            The power of the signal
        """
        lp = self.fs_bands[band][0]
        hp = self.fs_bands[band][1]
        if l == 0 and h != 0:
            if lp < h < hp:
                hp = h
            elif h < hp:
                return 0
        elif h == 0 and l != 0:
            if lp < l < hp:
                lp = l
            elif l > lp:
                return 0
        elif l != 0 and h != 0:
            if lp < h < hp:
                hp = h
            elif h < hp:
                return 0
            if lp < l < hp:
                lp = l
            elif l > lp:
                return 0
        filt_bufs = deepcopy(sig[s:f])

        # Get real amplitudes of FFT (only in postive frequencies)
        fft_vals = np.absolute(np.fft.rfft(filt_bufs))

        # Get frequencies for amplitudes in Hz
        fft_freq = np.fft.rfftfreq(len(filt_bufs), 1.0 / fs)
        # for band in eeg_bands:
        freq_ix = np.where((fft_freq >= lp) &
                    (fft_freq <= hp))[0]
        eeg_band_fft = np.mean(fft_vals[freq_ix] ** 2)

        return eeg_band_fft

    def get_power(self, sig, s, f, lp, hp, fs):
        """ Returns power for all bands.

        Args:
            sig: the signal
            s: where to start in samples
            f: where to end in samples
            lp: low pass fs of filter
            hp: high pass fs of filter
            fs: the fs of the signal
        Returns:
            alpha, beta, theta, gamma, delta
        """
        bands =  self.fs_bands.keys()
        ret = {}
        for b in bands:
            ret[b] = self._get_power_for_band(sig, s, f, b, lp, hp, fs)

        return ret
