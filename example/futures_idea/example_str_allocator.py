oldstr = str


class StrAllocator(str):
    oldstr = None

    def __new__(cls, *args, **kwargs):
        # return StrAllocator.oldstr.__new__(cls, *args, **kwargs)
        return oldstr.__new__(cls, *args, **kwargs)

    @property
    def __class__(self):
        return str


def patch_str_allocations():
    import builtins

    # StrAllocator.oldstr = str
    builtins.str = StrAllocator
