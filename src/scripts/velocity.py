import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from oem import OrbitEphemerisMessage
from skyfield.api import load, utc

from astro_pi_executor.resources.utils import get_resource

df_filename = "comparison.csv"
ts = load.timescale()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_using_oem():
    ephem = OrbitEphemerisMessage.open(get_resource("ISS.OEM_J2K_EPH.txt"))

    velocity = ephem.states[0].velocity
    speed = np.linalg.norm(velocity)

    logger.info(f"velocity: {velocity}")
    logger.info(f"speed: {speed}")
    return ephem


def calculate_using_tle():
    satellites = load.tle_file("iss_tle.txt")
    by_name = {sat.name: sat for sat in satellites}
    sat = by_name["ISS (ZARYA)"]

    instant = sat.at(ts.utc(2023, 7, 6, 14, 57, 30.2))
    velocity = instant.velocity.km_per_s
    speed = np.linalg.norm(velocity)  # type: ignore

    logger.info(f"velocity: {velocity}")
    logger.info(f"speed: {speed}")


logging.info("Using OEM: ")
calculate_using_oem()

logging.info("Using latest TLE: ")
calculate_using_tle()


def compare():
    if Path(df_filename).exists():
        df = pd.read_csv(df_filename, parse_dates=["Time"])
        df.set_index([0], in_place=True)
    else:
        ephem = OrbitEphemerisMessage.open("ISS.OEM_J2K_EPH.txt")
        satellites = load.tle_file("iss_tle.txt")
        by_name = {sat.name: sat for sat in satellites}
        sat = by_name["ISS (ZARYA)"]

        df_as_dict = {}

        for state in ephem.states:
            state_datetime = datetime.strptime(
                state._to_string().split()[0], "%Y-%m-%dT%H:%M:%S.%f"
            )
            state_datetime = state_datetime.replace(tzinfo=utc)
            instant = sat.at(ts.from_datetime(state_datetime))
            df_as_dict[state_datetime] = state.velocity, instant.velocity.km_per_s

        df = pd.DataFrame.from_dict(
            df_as_dict, orient="index", columns=["OEM Velocity", "TLE Velocity"]
        )
        df["OEM Speed"] = df["OEM Velocity"].apply(np.linalg.norm)
        df["TLE Speed"] = df["TLE Velocity"].apply(np.linalg.norm)
        df["Difference"] = df["OEM Speed"] - df["TLE Speed"]
        df["Error"] = (abs(df["Difference"]) / df["OEM Speed"]) * 100
    return df
