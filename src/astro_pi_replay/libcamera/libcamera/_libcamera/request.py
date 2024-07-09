import enum
import errno

from typing import Dict

from .controls.controls import ControlId, ControlList
from .framebuffer import FrameBuffer
from .stream import Stream
from .helpers import pyToControlValue


BufferMap = Dict[Stream, FrameBuffer]

class Status(enum.Enum):
    RequestPending = 0
    RequestComplete = 1
    RequestCancelled = 2
    Complete = RequestComplete

class Reuse(enum.Enum):
    Default = 0
    ReuseBuffers = 1

# Based on src/py/libcamera/py_main.cpp
# and libcamera/internal/request.h
# and include/libcamera/request.h
class Request:

    Status = Status
    Reuse = Reuse

    def __init__(self, cookie: int = 0) -> None:
        # the real Python implementation does not have a
        # public constructor defined, but the C++ constructor
        # is: 
        #   Request(Camera *camera, uint64_t cookie = 0);
        #
        self.bufferMap_: BufferMap = {}
        self.cookie_: int = cookie
        self.controls_: ControlList = {}
        self.metadata_: ControlList = {}
        self.status: Status = Status.RequestPending
        self._reuse: Reuse = Reuse.Default
        self._pending: set[FrameBuffer] = set()
        self._sequence: int = 0

    def add_buffer(self, stream: Stream, buffer: FrameBuffer) -> int:
        if stream in self.bufferMap_:
            return -errno.EEXIST
        buffer.set_request(self)
        self._pending.add(buffer)
        self.bufferMap_[stream] = buffer

        return 0

    def _reset(self):
        self._sequence = 0
        # cancelled_ = False
        # prepared_ = False;
        self._pending = set()
        # notifiers_.clear();
        # timer_.reset();


    @property
    def buffers(self) -> BufferMap:
        return self.bufferMap_

    @property
    def cookie(self) -> int:
        return self.cookie_


    @property
    def sequence(self) -> int:
        return self._sequence

    def has_pending_buffers(self):
        return len(self._pending) == 0

    def set_control(self, id: ControlId, value: object):
        self.controls_[id.id] = pyToControlValue(value, id.type)

    @property
    def metadata(self) -> ControlList:
        return self.metadata_

    def reuse(self, flags: Reuse = Reuse.ReuseBuffers) -> None:

        self._reset()

        if flags == Reuse.ReuseBuffers:
            for buffer in self.bufferMap_.values():
                buffer.set_request(self)
                self._pending.add(buffer)
        else:
            self.bufferMap_ = {}

        self.status = Status.RequestPending
        
        self.controls_ = {}
        self.metadata_ = {}

