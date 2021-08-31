class EegInfo():
    """ Data structure for holding an EEGs information """

    def __init__(self):
        self.edf_fn = ''
        self.name = ''
        self.file_duration = 0
        self.nsamples = 0
        self.label_list = []
        self.labels2chns = {}
        self.chns2labels = {}
        self.nchns = 0
        self.annotations = []
        self.fs = 0
        self.window_starts = []
        self.window_ends = []
        self.time_axis = []
        self.has_sz_idx = False
        self.sz_starts = []
        self.sz_ends = []
        self.has_ta = False
        self.pt_number = 0

    def __str__(self):
        return ("edf_fn:{edf_fn}\n"
                "name:{name}\n"
                "file_duration:{duration}\n"
                "nsamples:{nsamples}\n"
                "nchns:{nchns}\n"
                "fs:{fs}\n"
                "label_list:{ll}\n"
                "has_sz_idx:{sz}\n"
                "sz_starts:{starts}\n"
                "sz_ends:{ends}\n"
                "has_time_axis:{ta}\n"
                "pt_number:{pn}\n"
                ).format(edf_fn=self.edf_fn, name=self.name,
                         duration=self.file_duration, nsamples=self.nsamples,
                         nchns=self.nchns, fs=self.fs, ll=self.label_list,
                         sz=self.has_sz_idx, starts=self.sz_starts,
                         ends=self.sz_ends, ta=self.has_ta, pn=self.pt_number)

    def set_sz_idx(self, sz_idx):
        self.sz_idx = sz_idx
        self.has_sz_idx = True

    def set_time_axis(self, ta):
        self.time_axis = ta
        self.has_ta = True
