import collections
import enum

# Type synonyms
RGBC = tuple[int, int, int, int]
RGB = tuple[int, int, int]
RollPitchYawDict = dict[str, float]
XYZDict = dict[str, float]
InputEvent = collections.namedtuple('InputEvent', ('timestamp', 'direction', 'action'))

class ExecutionMode(str, enum.Enum):
    REPLAY = "REPLAY",
    LIVE = "LIVE"

