import wxdata
from wxdata.products import all_products
from wxdata.readers import decompress
from copy import deepcopy
import os
import glob
import pickle
from tqdm import tqdm

class File:
    def __init__(self, filename):
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
        relpath = os.path.relpath(self.filename, start=path)
        self.filename = relpath

    def make_absolute(self, path):
        self.filename = os.path.join(path, self.filename)

    def open(self):
        if self.product is None:
            raise Exception("Cannot open file: Product is unknown.")

        filename, artifact = decompress(self.filename)
        product_class = getattr(wxdata.products, self.product)
        product = product_class(filename)
        product.artifact = artifact
        return product

    def __repr__(self):
        return self.product.__name__ + " file: " + self.filename

class Index:

    def __init__(self):
        self._files = {}

    @property
    def products(self):
        return self._files.keys()
        pass

    def open(self, product, index):
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
        files = glob.glob(os.path.join(path, "**", "*"), recursive=True)
        print("Found {} files.".format(len(files)))
        for f in tqdm(files):
            f = File(f)
            if f.product:
                if not f.product in self._files:
                    self._files[f.product] = []
                self._files[f.product] += [f]

    def store(self, path):
        path = os.path.expanduser(path)
        dir = os.path.abspath(os.path.dirname(path))

        index = deepcopy(self)
        for k in index._files:
            for f in index._files[k]:
                f.make_relative(dir)

        pickle.dump(index, open(path, "wb"))

    @staticmethod
    def load(path):
        path = os.path.expanduser(path)
        dir = os.path.abspath(os.path.dirname(path))
        index =  pickle.load(open(path, "rb"))

        for k in index._files:
            for f in index._files[k]:
                f.make_absolute(dir)

        return index


path = "/home/simonpf/Dendrite/SatData/CloudSat/2B-GEOPROF.R04/"
index = Index()
index.generate(path)



