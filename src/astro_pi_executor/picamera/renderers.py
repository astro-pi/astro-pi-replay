import logging
from typing import TYPE_CHECKING, BinaryIO, Optional

from astro_pi_executor.custom_types import XYWH

if TYPE_CHECKING:
    # trick to avoid circular imports
    from astro_pi_executor.picamera.picamera_public_api import PiCameraPublicAPI

logger = logging.getLogger(__name__)


class PiRendererPublicAPI:
    def __init__(
        self,
        parent: "PiCameraPublicAPI",
        layer: int = 2,
        alpha: int = 255,
        fullscreen: bool = True,
        window: Optional[XYWH] = None,
        crop: Optional[XYWH] = (0, 0, 0, 0),
        rotation: int = 0,
        vflip: bool = False,
        hflip: bool = False,
    ) -> None:
        self.parent = parent
        self.layer = layer
        self.alpha = alpha
        self.fullscreen = fullscreen
        self.window = window
        self.crop = crop
        self.rotation = rotation
        self.vflip = vflip
        self.hflip = hflip

    def close(self) -> None:
        pass


class PiOverlayRendererPublicAPI(PiRendererPublicAPI):
    def __init__(
        self,
        parent: "PiCameraPublicAPI",
        source: BinaryIO,
        resolution: Optional[tuple[int, int]] = None,
        format: Optional[str] = None,
        layer: int = 0,
        alpha: int = 255,
        fullscreen: bool = True,
        window: Optional[XYWH] = None,
        crop: Optional[XYWH] = None,
        rotation: int = 0,
        vflip: bool = False,
        hflip: bool = False,
    ) -> None:
        self.source = source
        self.resolution = resolution
        self.format = format
        super().__init__(
            parent, layer, alpha, fullscreen, window, crop, rotation, vflip, hflip
        )

    def update(self, source: BinaryIO) -> None:
        self.source = source


class PiPreviewRendererPublicAPI(PiRendererPublicAPI):
    def __init__(
        self,
        parent: "PiCameraPublicAPI",
        source: BinaryIO,
        resolution=None,
        layer=2,
        alpha=255,
        fullscreen=True,
        window=None,
        crop=None,
        rotation=0,
        vflip=False,
        hflip=False,
    ) -> None:
        self.source = source
        self.resolution = resolution

        super_args = [parent, layer, alpha, fullscreen, window]
        if crop is not None:
            super_args.append(crop)
        super_args.extend([rotation, vflip, hflip])
        super().__init__(*super_args)


class PiNullSink:
    def __init__(self, parent: "PiCameraPublicAPI", source: BinaryIO) -> None:
        self.parent = parent
        self.source = source

    def close(self) -> None:
        pass
