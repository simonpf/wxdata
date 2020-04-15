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
        from pyhdf.SD import SD, SDC
        self.filename = filename
        self.file_handle = SD(self.filename, SDC.READ)

    def __del__(self):
        self.file_handle.end()
