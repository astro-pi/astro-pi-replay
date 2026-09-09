from dataclasses import dataclass


@dataclass
class RuntimeState:
    """
    The runtime state of the pre-executor environment
    """

    is_offline = False


state = RuntimeState()
