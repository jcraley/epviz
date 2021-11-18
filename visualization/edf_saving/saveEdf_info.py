""" Module for the infomation needed for the edf header """
import datetime
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP",
          "OCT","NOV","DEC"]

class SaveEdfInfo():
    """ Data structure for holding information for saving to edf namely
        the anonymized header """

    def __init__(self):
        """ Header parameters set to default values """
        self.fn = "" # Full file path to load in header
        self.pt_id = "X X X X" + " " * 73
        self.rec_info = "Startdate X X X X" + " " * 63
        self.start_date = "01.01.01"
        self.start_time = "01.01.01"
        self.py_h = 2
        self.pyedf_header = {'technician': '', 'recording_additional': '', 'patientname': '',
                        'patient_additional': '', 'patientcode': '', 'equipment': '',
                        'admincode': '', 'gender': '',
                        'startdate': datetime.datetime(2001, 1, 1, 1, 1, 1),
                        'birthdate': ''}

    def convert_to_header(self):
        """
        Converts from native EDF format:
        self.data.pt_id = file[8:88].decode("utf-8")
        self.data.rec_info = file[88:168].decode("utf-8")
        self.data.start_date = file[168:176].decode("utf-8")
        self.data.start_time = file[176:184].decode("utf-8")
        To a header dict for pyedflib
        """
        pt_id_fields = self.pt_id.split(" ")
        rec_info_fields = self.rec_info.split(" ")

        self.pyedf_header['patientcode'] = pt_id_fields[0]
        self.pyedf_header['gender'] = pt_id_fields[1]
        if pt_id_fields[2] != "X":
            month = MONTHS.index(pt_id_fields[2].split("-")[1]) + 1
            self.pyedf_header['birthdate'] = datetime.datetime(int(pt_id_fields[2].split("-")[2]),
                                                        month, int(pt_id_fields[2].split("-")[0]))
        else:
            self.pyedf_header['birthdate'] = ""
        self.pyedf_header['patientname'] = pt_id_fields[3]
        if len(pt_id_fields) > 4:
            self.pyedf_header['patient_additional'] = "".join(pt_id_fields[4:])
        else:
            self.pyedf_header['patient_additional'] = ""

        self.pyedf_header['admincode'] = rec_info_fields[2]
        self.pyedf_header['technician'] = rec_info_fields[3]
        self.pyedf_header['equipment'] = rec_info_fields[4]
        if len(rec_info_fields) > 5:
            self.pyedf_header['recording_additional'] = "".join(rec_info_fields[5:])
        else:
            self.pyedf_header['recording_additional'] = ""

        year = int(self.start_date.split(".")[2])
        if year > 30:
            year += 1900
        else:
            year += 2000
        start_date = self.start_date.split(".")
        start_time = self.start_time.split(".")
        self.pyedf_header['startdate'] = datetime.datetime(year,
                                            int(start_date[1]),
                                            int(start_date[0]),
                                            int(start_time[0]),
                                            int(start_time[1]),
                                            int(start_time[2]))
