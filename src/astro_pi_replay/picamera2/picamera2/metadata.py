"""
Copied from picamera2 commit e6c6d9232eaee5a1d4ec9178d9694a5554c1b0db
under a BSD 2-Clause License.
"""


class Metadata:
    def __init__(self, metadata={}):
        self.__dict__ = metadata.copy()

    def __repr__(self):
        return f"<Metadata: {self.__dict__}>"

    def make_dict(self):
        return self.__dict__.copy()
