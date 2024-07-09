import logging
import os
import tempfile
from typing import BinaryIO

logger = logging.getLogger(__name__)

# Libcamera C++ classes
class UniqueFD:
    """Libcamera UniqueFD Class"""

    def __init__(self, fd=-1):
        if isinstance(fd, UniqueFD):
            self.__fd = fd.release()
        else:
            self.__fd = fd

    def release(self):
        fd = self.__fd
        self.__fd = -1
        return fd

    def get(self):
        return self.__fd

    def isValid(self):
        return self.__fd >= 0


class DmaHeap:

    _fds: dict[tuple[str,int], BinaryIO] = {}

    def __init__(self) -> None:
        logger.info("Not using real dma heaps")

    def alloc(self, name, size) -> UniqueFD:
        if (name,size) not in DmaHeap._fds:
            fd = tempfile.TemporaryFile()
            os.ftruncate(fd.fileno(), size)
            DmaHeap._fds[(name,size)] = fd
        fd = DmaHeap._fds.get((name,size))
        if fd:
            return UniqueFD(fd.fileno())
        else:
            return UniqueFD()

