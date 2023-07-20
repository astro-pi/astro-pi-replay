class PiCameraError(Exception):
    pass


class PiCameraRuntimeError(RuntimeError):
    pass


class PiCameraValueError(PiCameraError, ValueError):
    pass


class PiCameraWarning(Warning):
    """
    Base class for PiCamera warnings.
    """


class PiCameraDeprecated(PiCameraWarning, DeprecationWarning):
    """
    Raised when deprecated functionality in picamera is used.
    """


class PiCameraFallback(PiCameraWarning, RuntimeWarning):
    """
    Raised when picamera has to fallback on old functionality.
    """
