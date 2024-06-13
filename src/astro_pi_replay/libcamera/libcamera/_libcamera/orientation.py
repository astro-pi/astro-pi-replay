import enum


class Orientation(enum.Enum):
    """
    Derived from include/libcamera/orientation.h
    """

    Rotate0 = 1
    Rotate0Mirror = 2
    Rotate180 = 3
    Rotate180Mirror = 4
    Rotate90Mirror = 5
    Rotate270 = 6
    Rotate270Mirror = 7
    Rotate90 = 8
