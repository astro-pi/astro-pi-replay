class StrDispatcher:
    _subclasses = dict()

    def __new__(cls, *args, dispatch_arg, **kwargs):
        print(f"Dispatch arg: {dispatch_arg}")
        # dispatch to a registered child class
        subcls = cls.getsubcls(dispatch_arg)
        return super(StrDispatcher, subcls).__new__(subcls)

    def __init_subclass__(subcls, **kwargs):
        print("Inside init subclass")
        super(StrDispatcher, subcls).__init_subclass__(**kwargs)

        # add __new__ contructor to child class based on default first dispatch argument
        def __new__(cls, *args, dispatch_arg=subcls.__qualname__, **kwargs):
            return super(StrDispatcher, cls).__new__(cls, *args, **kwargs)

        subcls.__new__ = __new__
        StrDispatcher.register_subclass(subcls)

    @classmethod
    def getsubcls(cls, key):
        print("Inside getsubcls")
        name = cls.__qualname__
        if cls is not StrDispatcher:
            raise AttributeError(f"type object {name!r} has no attribute 'getsubcls'")
        try:
            return StrDispatcher._subclasses[key]
        except KeyError:
            raise KeyError(
                f"No child class key {key!r} in the "
                f"{cls.__qualname__} subclasses registry"
            )

    @classmethod
    def register_subclass(cls, subcls):
        print("Inside register_subclass")
        name = subcls.__qualname__
        if cls is not StrDispatcher:
            raise AttributeError(
                f"type object {name!r} has no attribute " f"'register_subclass'"
            )
        if name not in StrDispatcher._subclasses:
            StrDispatcher._subclasses[name] = subcls
        else:
            raise KeyError(f"{name} subclass already exists")

    def join(self):
        print("meow")


class Child(StrDispatcher):
    def join(self):
        print("Woof")

    pass


c1 = StrDispatcher(dispatch_arg="Child")
assert isinstance(c1, Child)
c2 = Child()
assert isinstance(c2, Child)
