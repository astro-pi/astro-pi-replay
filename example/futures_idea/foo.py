from hat_v2 import FunkyString

import logging

logging.basicConfig(level=logging.DEBUG)

print(FunkyString(",").join(["Foo", "bar"]))
