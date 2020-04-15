import re
from wxdata.products.common import Hdf4File

class DardarCloud(Hdf4File):

    pattern = re.compile("DARDAR-CLOUD_v[\d\.]*_([\d]*)_([\d]*)\.*")
    filename_pattern = "DARDAR-CLOUD_v{version}_{start_time}_{number}"

    def __init__(self,
                 filename,
                 artifact=None):
        super().__init__(filename)

    @property
    def start_time(self):
        return None

    @property
    def end_time(self):
        return None

    @property
    def granule(self):
        return None
