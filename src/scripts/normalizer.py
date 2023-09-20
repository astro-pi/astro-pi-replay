"""
Normalizes the column names of sense hat
"""

import pandas as pd

df = pd.read_csv("AstroX/data.csv", parse_dates=["datetime"])

name_to_new_name = {
    # "temp": "temp",
    # "pres": "pres",
    # "hum": "hum",
    # "red": "red",
    # "green": "green",
    # "blue": "blue",
    # "clear": "clear",
    # "mag_x": "mag_x",
    # "mag_y": "mag_y",
    # "mag_z": "mag_z",
    # "acc_x": "acc_x",
    # "acc_y": "acc_y",
    # "acc_z": "acc_z",
    # "gyro_x": "gyro_x",
    # "gyro_y": "gryo_y",
    # "gyro_z": "gyro_z",
    # "datetime": "datetime",
    # TODO need to figure this out.
    "yaw",
    "pitch",
    "roll",
}
