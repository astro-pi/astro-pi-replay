from threading import Lock
import time
import logging
from typing import Iterable, Any
import re


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MyFuture(str):
    def __init__(self, value):
        self.value = value
        self._complete_lock = Lock()
        self._complete = False
        logger.debug(f"Initialised future {value}")

    def __add__(self):
        logger.debug("Add called")

    def _set_complete(self):
        with self._complete_lock:
            self._complete = True
        logger.debug("Future is now complete")

    def is_complete(self) -> bool:
        with self._complete_lock:
            return self._complete

    def __getattr__(self, name):
        logger.debug("Inside getattr - called unconditionally")

    def __get__(self):
        logger.debug("Inside get")

    def __repr__(self):
        logger.debug("Inside __repr__. Calling me should evaluate the Future")
        self.block_until_complete()
        return repr(self.value)

    def join(self, iterable):
        logger.debug("Inside join")
        return super().join(iterable)

    def get(self):
        if not self.is_complete():
            raise Exception("Future not yet complete")
        with self._complete_lock:
            return self.value

    def block_until_complete(self):
        if not self.is_complete():
            time.sleep(5)
            self._set_complete()
        # while not self.is_complete():
        #    pass


# class SenseHat:
#
#    def __init__(self):
#        pass
#
#    def get_compass(self) -> MyFuture:
#        """Submits a reading to the reader"""
#        return MyFuture("compass")

# Should evaluate when a _side-effect_ is called e.g. print, log, or file.write

# __builtins__.print = custom_print
# __builtins__.list = custom_print
# __builtins__.set = custom_print

f1 = MyFuture("1")
f2 = MyFuture("2")
example_futures = [f1, f2]


def my_funky_join(delimiter: str, iterable: Iterable[Any]):
    logger.debug("Inside my_funky_join")
    return delimiter.join(map(str, iterable))


class FunkyMeta(type):
    def __new__(cls, name, bases, dct):
        return super.__new__(cls)

    # def __repr__(self):
    #     return repr(str)


class FunkyString2(str):
    """
    Overridden to control the join method to ensure
    that any Future types block until they are completed.

    The join method is often called when saving sense hat data
    together
    """

    def join(self, iterable: Iterable[Any]):
        logger.debug("Inside join")
        for item in iterable:
            logger.debug(type(item))
        return super().join(iterable)


class FunkyString(str):
    """
    Overridden to control the join method to ensure
    that any Future types block until they are completed.

    The join method is often called when saving sense hat data
    together
    """

    def join(self, iterable: Iterable[Any]):
        logger.debug("Inside join")
        for item in iterable:
            logger.debug(type(item))
        return super().join(iterable)


class S:
    """
    Given a python file, converts strings to FunkyStrings
    A preprocessor
    """

    # 1. Parse the Python file(s) for literal strings "" and '' that are not """ and '''

    # https://stackoverflow.com/questions/768634/parse-a-py-file-read-the-ast-modify-it-then-write-back-the-modified-source-c#:~:text=You%20can%20parse%20the%20python,execute%20it%20as%20shown%20above.

    def sub(self, file: str):
        with open(file) as f:
            lines = f.readlines()

        # TODO make more efficient
        lines = [re.sub(r"'([^']+)'", r"FunkyString('\1')", line) for line in lines]
        lines = [re.sub(r'"([^"]+)"', r'FunkyString("\1")', line) for line in lines]
        newlines = []
        for line in lines:
            print(line, type(line))
            x = re.sub("Foo", "Bar", line)
            print(x)
            newlines.append(x)

        # lines = [re.sub(r"'([^']+)'", 'FunkyString("\1"h', line) for line in lines]
        return "".join(newlines)


class FunkyType(type):
    def __new__(cls, arg):
        logger.debug("inside __new__")
        logger.debug(f"Arg given: {arg}")
        return object.__new__(cls)


# def funky_type(original_type):
#     def _funky_type(type_to_check):
#         if original_type(type_to_check) is MyFuture:
#             return original_type("")


example_file = "../uses_sense_hat.py"
# import builtins

# builtins.str = FunkyString # covers the str() method
# ",".join(example_futures)
# builtins.type = FunkyType

# See:
# https://stackoverflow.com/questions/20583138/is-it-possible-to-proxy-a-python-str-and-make-join-work
# https://stackoverflow.com/questions/50667128/is-it-possible-to-fully-monkey-patch-builtin-str-in-python3
