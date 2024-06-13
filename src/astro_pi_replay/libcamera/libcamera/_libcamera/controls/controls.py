"""
Derived from include/libcamera/controls.h
"""
import enum
from typing import Optional, Dict, List


class ControlType(enum.Enum):
    Null = 0
    Bool = 1
    Byte = 2
    Integer32 = 3
    Integer64 = 4
    Float = 5
    String = 6
    Rectangle = 7
    Size = 8


class ControlId:
    def __init__(self, id: int, name: str, type_: ControlType) -> None:
        self.id: int = id
        self.name: str = name
        # suffixed with underscore since type is a reserved word
        self.type_: ControlType = type_


class ControlValue:
    def __init__(self, t: object) -> None:
        self.type_: ControlType = ControlType.Null
        self.numElements_: int = 0
        self.value_: object = t


class ControlInfo:
    def __init__(
        self,
        min: ControlValue,
        max: ControlValue,
        # def is reserved keyword, hence add trailing underscore
        default: Optional[ControlValue] = None,
    ):
        self.min = min
        self.max = max
        self.default = default

    def __str__(self) -> str:
        return f"[{self.min.value_}..{self.max.value_}]"

ControlInfoMap = Dict[ControlId, ControlInfo]
ControlList = List[ControlValue]
