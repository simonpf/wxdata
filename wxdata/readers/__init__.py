import atexit
import tempfile
import os
import zipfile

################################################################################
# Temporary file storage
################################################################################

_folder = tempfile.TemporaryDirectory()

def cleanup():
    try:
        global _folder
        os.rmdir(_folder.name)
    except:
        pass
atexit.register(cleanup)

################################################################################
# Zip file.
################################################################################

class ZipReader():
    def __init__(self, filename):
        with zipfile.ZipFile(filename, 'r') as zipf:
            member = zipf.namelist()[0]
            zipf.extract(member, path=_folder.name)

        self.filename = os.path.join(_folder.name, member)

    def __del__(self):
        os.remove(self.filename)

################################################################################
# Decompression.
################################################################################

def decompress(filename):
    _, ext = os.path.splitext(filename)
    if ext[-3:] in ["zip", "ZIP"]:
        artifact = ZipReader(filename)
        return artifact.filename, artifact
    else:
        return filename, None
