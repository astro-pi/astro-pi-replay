"""
Example of how to upsample sense hat values
"""
import pandas as pd

df = pd.read_csv("...")
df2 = df.copy()
# Round up datetime to the nearest second
df2.index = df2.index.round("1S")
# Upsample the dataframe into every second and interpolate intermediate values
df3 = df2.resample("1S").interpolate(method="linear")

# TODO - ensure the data types remain correct
