import os
import sys
import logging

logger = logging.getLogger(__name__)


def nonblocking_pipe() -> tuple[int, int]:
    """
    Creates a non-blocking pipe if possible, else
    throws a RuntimeError.
    Returns a tuple containing the read and write
    file descriptors.
    """
    r: int
    w: int
    if hasattr(os, "pipe2") and hasattr(os, "O_NONBLOCK"):
        r, w = os.pipe2(os.O_NONBLOCK)
    elif sys.platform == "emscripten":
        # emscripten is non blocking by default
        r, w = os.pipe()
    elif sys.platform == "win32":
        # TODO - see https://stackoverflow.com/questions/34504970/non-blocking-read-on-os-pipe-on-windows
        # from python 3.12 onwards, can use set_blocking(r, False)
        raise RuntimeError("Not yet implemented")
    else: 
        try:
            import fcntl
            r, w = os.pipe()
            # set the O_NONBLOCK 
            flags = fcntl.fcntl(r, fcntl.F_GETFL)
            fcntl.fcntl(r, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        except (ImportError, AttributeError):
            # TODO make Astro Pi Replay exception
                raise RuntimeError("Cannot support this")

    return r, w
