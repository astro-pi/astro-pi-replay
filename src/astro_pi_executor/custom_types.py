import collections
from enum import Enum

# Type synonyms
RGBC = tuple[int, int, int, int]
RGB = tuple[int, int, int]
RollPitchYawDict = dict[str, float]
XYZDict = dict[str, float]
InputEvent = collections.namedtuple("InputEvent", ("timestamp", "direction", "action"))
XYWH = tuple[float, float, float, float]
UV = tuple[int, int]


DEFAULT_ROLL_PITCH_YAW_DICT = {"roll": float(), "pitch": float(), "yaw": float()}
DEFAULT_RGB_TUPLE = (int(), int(), int())
DEFAULT_RGBC_TUPLE = (int(), int(), int(), int())
DEFAULT_X_Y_Z_DICT = {"x": float(), "y": float(), "z": float()}
DEFAULT_XYWH = (0.0, 0.0, 1.0, 1.0)
DEFAULT_CALLABLE = (
    lambda x: x
)  # TODO could use inspect module to check type annotations at runtime


class ExecutionMode(str, Enum):
    REPLAY = ("REPLAY",)
    LIVE = "LIVE"
