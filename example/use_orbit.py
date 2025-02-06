from orbit import ISS
from pathlib import Path

cur_dir = Path(__file__).parent
out_file = cur_dir / "foo.txt"
with out_file.open("w") as f:
    f.write(repr(ISS().coordinates()))
