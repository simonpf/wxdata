import re
from datetime import datetime
from wxdata.products.common import Hdf4File

def cloudsat_parse_time(s):
    return datetime.strptime(s, "%Y%m%d%H%M%S")

class CloudSatBase(Hdf4File):

    def __init__(sefl, filename):
        super().__init__(filename)

    @property
    def start_time(self):
        ts = self.file_handle.attributes()["start_time"]
        return cloudsat_parse_time(ts)

    @property
    def end_time(self):
        ts = self.file_handle.attributes()["end_time"]
        return cloudsat_parse_time(ts)


class CloudSat_1b_CPR(CloudSatBase):

    pattern = re.compile("([\d]*)_([\d]*)_CS_1B-CPR_GRANULE_P_R([\d]*)_E([\d]*)\.*")

    def __init__(self, filename):
        super().__init__(filename)

class CloudSat_2b_GeoProf(CloudSatBase):

    pattern = re.compile("([\d]*)_([\d]*)_CS_2B-GEOPROF_GRANULE_P_R([\d]*)_E([\d]*)\.*")

    def __init__(self, filename):
        super().__init__(filename)
