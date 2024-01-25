This is a modified `setup.py` taken from [python-sgp4](https://github.com/brandon-rhodes/python-sgp4).

It removes the C++ code (which is just an optimisation rather than functionally necessary) so that the wheel produced results in a Python-only build, which makes it easier to use in Pyodide.
