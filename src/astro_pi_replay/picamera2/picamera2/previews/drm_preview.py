from .common import UNSUPPORTED_PREVIEW_TYPE_MESSAGE

class DrmPreview:

    def __init__(self,*args,**kwargs) -> None:
        raise RuntimeError(UNSUPPORTED_PREVIEW_TYPE_MESSAGE)
