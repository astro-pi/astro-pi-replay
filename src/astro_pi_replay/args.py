from dataclasses import dataclass
from pathlib import Path
from typing import (
    Annotated,
    Callable,
    Optional,
    Union,
    Any,
    Iterable,
    Annotated,
)
import argparse


parser = argparse.ArgumentParser()

def negate(x):
    return not x

@dataclass
class FieldCLIMetadata:
    name: Annotated[str, "ignore"]
    help: str
    action: Union[None,str,type[argparse.Action]] = None
    dest: Optional[str] = None
    type: Union[None,Any] = None
    choices: Union[None,Iterable[Any]] = None

    _append_default_to_help: Annotated[bool, "ignore"] = True
    _map_help_default: Annotated[Optional[Callable[[Any],Any]],
                                 "ignore"] = None

field_metadata: dict[str,FieldCLIMetadata] = {
    "interpolate_sense_hat": FieldCLIMetadata(
        name="--interpolate-sense-hat-values",
        action=argparse.BooleanOptionalAction,
        dest="interpolate_sense_hat",
        help="Whether to interpolate measurements from " +
            "the sense hat.",
    ),
    "no_wait_images": FieldCLIMetadata(
        name="--match-original-photo-intervals",
        action=argparse.BooleanOptionalAction,
        help="Whether to sleep in between successive " +
            "captures to try and match the " +
            "timestamps of the original photos.",
        # because no_wait_images is not in 'positive' form
        _map_help_default=negate
    ),
    "sequence": FieldCLIMetadata(
        name="--sequence",
        help="The sequence id to use in replays."
    ),
        "snapshot_sense_hat_display": FieldCLIMetadata(
        name="--snapshot-sense-hat-display",
        action=argparse.BooleanOptionalAction,
        help="Whether to save snapshots of the SenseHat " +
            "display to --sense-hat-snapshot-dir."
    ),
        "sense_hat_snapshot_dir": FieldCLIMetadata(
        "--sense-hat-snapshot-dir",
        type=Path,
        help="The directory in which to save " +
            "snapshots of the SenseHat display. "
            "Defaults to the current directory.",
        _append_default_to_help=False
    ),
    "is_transparent_to_user": FieldCLIMetadata(
        name="--is-transparent-to-user",
        action=argparse.BooleanOptionalAction,
        help="Whether to warn the user when a called " +
            "method or accessed attribute that would " +
            "work using the real hardware is not fully " +
            "implemented by the replay tool. " +
            "By default,  the replay tool continues " +
            "silently (as if it were transparent)."
    ),
    "streaming_mode": FieldCLIMetadata(
        name="--streaming-mode",
        action=argparse.BooleanOptionalAction,
        help="Whether to stream the image assets from " +
            "storage instead of bulk downloading prior " +
            "to running"
    ),
    "resolution": FieldCLIMetadata(
        name="--resolution",
        choices=((4056, 3040), (1280, 720)),
        help="The resolution of images to playback. " +
            "Default is (4056, 3040)."
    ),
    "photography_type": FieldCLIMetadata(
        name="--photography-type",
        choices=(("VIS", "IR")),
        help="Whether to playback visible light photos "
        + "(VIS) or infrared light (IR). Default is VIS.",
    ),
}
