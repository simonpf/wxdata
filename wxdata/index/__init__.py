import os
import glob
import pickle
from copy import deepcopy
from datetime import datetime
from tqdm import tqdm

import wxdata
from wxdata.products import all_products
from wxdata.readers import decompress

################################################################################
# FileRecord
################################################################################

class FileRecord:
    """
    A FileRecord hold a reference to an indexed data file. It holds
    the filename, name of the products class as well as start and
    end time.
    Attributes:
        product(:code:`str`): The name of the product class that the
            file belongs to. None if filename couldn't be associated
            to any product.
        start_time(:code:`datetime`): Timestamp of the first data entry
            in this file.
        end_time(:code:`datetime`): Timestamp of the last data entry
            in this file.
    """
    def __init__(self, filename):
        """
        Create a file record from a given file name.

        Determines the product type of the given filename and determines
        product attribute. If that was successful opens the file and
        extracts start and end time.

        Arguments:
            filename(:code:`str`): The filename of the file to index.
        """
        self.filename = filename
        for c in all_products:
            name = os.path.basename(filename)
            if c.pattern.match(name):
                self.product = c.__name__
                file = self.open()
                self.start_time = file.start_time
                self.end_time = file.end_time
                return None
        self.product = None

    def make_relative(self, path):
        """
        Converts filename attribute into a relative path.

        Arguments:
            path(:code:`str`): The reference path to use to determine
                the relative path.
        """
        relpath = os.path.relpath(self.filename, start=path)
        self.filename = relpath

    def make_absolute(self, path):
        """
        Converts filename attribute into a absolute path.

        Arguments:
            path(:code:`str`): The reference path to use to convert
                filename to relative path.
        """
        self.filename = os.path.join(path, self.filename)

    def open(self):
        """
        Open data product corresponding to this record.
        """
        if self.product is None:
            raise Exception("Cannot open file: Product is unknown.")

        filename, artifact = decompress(self.filename)
        product_class = getattr(wxdata.products, self.product)
        product = product_class(filename)
        product.artifact = artifact
        return product

    def __repr__(self):
        """
        Pretty printing of data record.
        """
        return self.product + " file: " + self.filename

################################################################################
# FileRecord
################################################################################

class Index:
    """
    A file index holding references and meta data of different data products.

    Attributes:
        products: List of products available from this index.
    """

    def __init__(self):
        """
        Create an index object.
        """
        self._files = {}

    @property
    def products(self):
        return self._files.keys()
        pass

    def open(self, product, index):
        """
        Open given product file.

        Arguments:
            product(:code:`str` or product class): String or product
                representing the product to select from the index.
            index(:code:`int`): Index of the file of the given type
                to open.

        Returns:
            Instance of the requested product type corresponding to
            the file at index :code:`index`.
        """
        product_names = [f.__name__ for f in all_products]
        if type(product) == str:
            if not product in product_names:
                raise Exception("{} is not a known data product."
                                .format(product))
            name = product
        else:
            if not product in all_products:
                raise Exception("{} is not a known data product."
                                .format(product))
            name = product.__name__

        if not name in self._files:
            raise ValueError("Product {} not available from this index."
                             .format(name))
        files = self._files[name]

        n = len(files)
        if index >= n:
            raise ValueError("Index {} exceeds available files.")

        return files[index].open()


    def generate(self, path):
        """
        Index file in folder tree.

        Recursively traverses sub-folders of the provided path and indexes
        all known data products.

        Arguments:
            path(:code:`str`): Root folder of the folder-tree to index.
        """
        path = os.path.expanduser(path)
        files = glob.glob(os.path.join(path, "**", "*"), recursive=True)
        print("Found {} files.".format(len(files)))
        for f in tqdm(files):
            f = FileRecord(f)
            if f.product:
                if not f.product in self._files:
                    self._files[f.product] = []
                self._files[f.product] += [f]

    def get_files(self, product, start=None, end=None):
        if not product in self.products:
            raise ValueError("{} is not available from this index. Available"
                             " products are {}.".format(self.products))

        if not (isinstance(start, datetime) or start is None):
            raise ValueError("start keyword argument must be a datetime object "
                             " or None.")

        if not (isinstance(end, datetime) or start is None):
            raise ValueError("end keyword argument must be a datetime object "
                             " or None.")

        files = self._files[product]
        if start is None and end is None:
            return files

        in_range = []
        for f in files:
            if not start is None and f.end_time >= start:
                if not end is None and f.start_time < end:
                    in_range += [f]

        return in_range

    def store(self, filename):
        """
        Store index to disc.

        Arguments:
            filename(:code:`str`): Filename to which to store the index.
        """
        filename = os.path.expanduser(filename)
        dir = os.path.abspath(os.path.dirname(filename))

        index = deepcopy(self)
        for k in index._files:
            for f in index._files[k]:
                f.make_relative(dir)

        pickle.dump(index, open(filename, "wb"))

    @staticmethod
    def load(filename):
        """
        Load index from disc.

        Arguments:
            filename(:code:`str`): Filename from which to load the index.
        """
        filename = os.path.expanduser(filename)
        dir = os.path.abspath(os.path.dirname(filename))
        index =  pickle.load(open(filename, "rb"))

        for k in index._files:
            for f in index._files[k]:
                f.make_absolute(dir)

        return index

    def __repr__(self):
        s = ":: wxdata file index ::\n"
        s += "\nAvailable products:"
        for p in self.products:
            s += "\n\t" + p
            s += " (" + str(len(self._files[p])) + ")"
        s += "\n"
        return s

index = Index.load("~/Dendrite/SatData/CloudSat/2b_geoprof.index")
