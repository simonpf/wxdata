import re
import os
import numpy as np
import numpy.ma as ma
from datetime import datetime, timedelta
from wxdata.products.common import Hdf4File

################################################################################
# CloudSatBase
################################################################################

class CloudSatBase(Hdf4File):
    """
    Base class for CloudSat files.
    """
    @staticmethod
    def name_to_date(name):
        name = os.path.basename(name)
        name = name.split("_")[0]
        return datetime.strptime(name, "%Y%j%H%M%S")

    def __init__(sefl, filename):
        super().__init__(filename)

    @property
    def start_time(self):
        """
        datetime object corresponding to the timestamp of the first profile
        in the file.
        """
        utc_start = self.vs.attach("UTC_start")[0]
        start_time = self.date + timedelta(seconds=utc_start[0])
        return start_time

    @property
    def end_time(self):
        """
        datetime object corresponding to the timestamp of the last profile
        in the file.
        """
        start_time = self.start_time
        dt = timedelta(seconds=self["Profile_time"][-1][0])
        return start_time + dt

    @property
    def date(self):
        """
        datetime object corresponding to 00:00:00 on the day of the first
        profile in the file.
        """
        date = self.__class__.pattern.match(os.path.basename(self.filename)).group(1)
        date = datetime.strptime(date, "%Y%j%H%M%S")
        return datetime(year=date.year, month=date.month, day=date.day)

    @property
    def latitude(self):
        return np.array(self["Latitude"][:], dtype=np.float16)

    @property
    def longitude(self):
        return np.array(self["Longitude"][:], dtype=np.float16)

    @property
    def altitude(self):
        return np.array(self["Height"][:], dtype=np.float16)

################################################################################
# Level 1b
################################################################################

class CloudSat_1b_CPR(CloudSatBase):
    """
    Class representing the CloudSat 1B CPR product [1]_.

    .. [1] http://www.cloudsat.cira.colostate.edu/data-products/level-1b/1b-cpr

    """
    pattern = re.compile("([\d]*)_([\d]*)_CS_1B-CPR_GRANULE_P_R([\d]*)_E([\d]*)\.*")

    def __init__(self, filename):
        """
        Args:
            filename(:code:`filename`): Full path of the HDF4 file containing the
                data.

        """
        super().__init__(filename)

################################################################################
# Level 2b
################################################################################

class CloudSat_2b_GeoProf(CloudSatBase):

    pattern = re.compile("([\d]*)_([\d]*)_CS_2B-GEOPROF_GRANULE_P_R([\d]*)_E([\d]*)\.*")

    def __init__(self, filename):
        """
        Args:
            filename(:code:`filename`): Full path of the HDF4 file containing the
                data.

        """
        super().__init__(filename)

    @property
    def radar_reflectivity(self):
        """
        Scaled and masked radar reflectivities.

        This property contains the radar reflectivities in dBZe units. Values
        have been divided with a factor of 100 w.r.t. to the raw data and
        missing values have been masked.

        In addition to this, values outside the range given in [1]_ are masked.
        """
        raw_data = self["Radar_Reflectivity"][:]
        data = np.array(raw_data, dtype=np.float32) / 100.0
        mask = raw_data <= -8888
        data = np.maximum(data, -40)
        data = np.minimum(data, 50)
        return ma.masked_array(data, mask=mask)

class CloudSat_Modis_Aux(CloudSatBase):

    pattern = re.compile("([\d]*)_([\d]*)_CS_MODIS-AUX_GRANULE_P_R([\d]*)_E([\d]*)\.*")

    def __init__(self, filename):
        """
        Args:
            filename(:code:`filename`): Full path of the HDF4 file containing the
                data.

        """
        super().__init__(filename)
