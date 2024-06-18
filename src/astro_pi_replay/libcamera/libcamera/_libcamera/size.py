from typing import Optional


class Size:
    #
    # Based on include/libcamera/geometry.h
    #

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def __lt__(self, other: "Size"):
        if self.width < other.width and self.height < other.height:
            return True
        elif self.width >= other.width and self.height >= other.height:
            return False

        area: int = self.width * self.height
        other_area: int = other.width * other.height

        if area < other_area:
            return True
        elif area > other_area:
            return False

        return self.width < other.width

    def __eq__(self, other: object):
        if not isinstance(other, Size):
            return False
        return self.width == other.width and self.height == other.height

    def __gt__(self, other: "Size"):
        return not self.__lt__(other) and not self.__eq__(other)


class SizeRange:
    min: Size
    max: Size
    hStep: int
    vStep: int

    def __init__(
        self,
        size: Optional[Size] = None,
        max_size: Optional[Size] = None,
        hstep: int = 0,
        vstep: int = 0,
    ):
        if size and max_size is None:
            self.min = size
            self.max = size
        if size and max_size:
            self.min = size
            self.max = size
        self.hStep = hstep
        self.vStep = vstep

    def contains(self, size: Size):
        if (
            size.width < self.min.width
            or size.width > self.max.width
            or size.height < self.min.height
            or size.height > self.max.height
            or (self.hStep and (size.width - self.min.width) % self.hStep)
            or (self.vStep and (size.height - self.min.height) % self.vStep)
        ):
            return False
        return True
