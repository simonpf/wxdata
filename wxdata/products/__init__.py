import re
from datetime import datetime
from abc import ABCMeta, abstractmethod

from wxdata.products.cloudsat import (CloudSat_1b_CPR, CloudSat_2b_GeoProf)
from wxdata.products.dardar import DardarCloud

all_products = [CloudSat_1b_CPR,
                CloudSat_2b_GeoProf,
                CloudSat_Modis_Aux]
