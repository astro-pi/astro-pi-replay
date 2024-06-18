import enum


class NoiseReductionModeEnum(enum.Enum):
    """
    TODO auto generate from
    src/libcamera/control_ids_draft.yaml
    """

    Off = 0
    Fast = 1
    HighQuality = 2
    Minimal = 3
    ZSL = 4
