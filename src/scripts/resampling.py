"""
Example of how to upsample sense hat values
"""
from datetime import datetime

import pandas as pd
import scipy as sp

df = pd.read_csv("...")
df2 = df.copy()
# Round up datetime to the nearest second
df2.index = df2.index.round("1S")
# Upsample the dataframe into every second and interpolate intermediate values
df3 = df2.resample("1S").interpolate(method="linear")

# TODO - ensure the data types remain correct


# Option 2: don't store the resampled data (since it would be have to be
# at a very granular resolution). Instead, just use scipy to do a simple
# interpolation function for each column :)


f = sp.interpolate.interp1d(
    df.index.map(datetime.timestamp), df["temp"].to_numpy(), kind="cubic"
)
d = datetime(2023, 4, 25, 8, 25, 45)
f(d.timestamp())  # estimated temp at this time
