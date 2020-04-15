from abc import ABCMeta, abstractmethod

class DataProductBase(metaclass=ABCMeta):

    def __init__(self):
        self._artifact = None

    @property
    def artifact(self):
        return self._artifact

    @artifact.setter
    def artifact(self, artifact):
        self._artifact = artifact


class Hdf4File(DataProductBase):
    """
    Base class for file products using HDF4File format. The :class:`Hdf4File`
    wraps around the pyhdf.SD class to implement RAII.
    """
    def __init__(self, filename):
        """
        Open an HDF4 file for reading.

        Arguments:

            filename(str): The path to the file to open.
        """
        super().__init__()
        from pyhdf.HDF import HDF, HC
        from pyhdf.SD import SD, SDC
        import pyhdf.VS
        self.filename = filename
        self.hdf = HDF(self.filename, HC.READ)
        self.vs = self.hdf.vstart()
        self.sd = SD(self.filename, SDC.READ)

    @property
    def vs_attributes(self):
        vs_attributes = [t[0] for t in self.vs.vdatainfo()]
        return vs_attributes

    @property
    def sd_attributes(self):
        sd_attributes = [t for t in self.sd.datasets()]
        return sd_attributes

    @property
    def attributes(self):
        return self.vs_attributes + self.sd_attributes

    def __getitem__(self, name):
        if name in self.vs_attributes:
            return self.vs.attach(name)
        elif name in self.sd_attributes:
            return self.sd.select(name)
        else:
            raise ValueError("{} is not a known attribute of this file.")

    def __del__(self):
        self.sd.end()
        self.vs.end()
        self.hdf.close()
