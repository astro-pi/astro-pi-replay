# This script will attempt to make the best match

from datetime import datetime, timedelta, timezone, time
from pathlib import Path
from typing import cast, Union
import json
import logging
import math
import re

import numpy as np
import pandas as pd
from skyfield.positionlib import Geocentric
from skyfield.api import load, Loader, Time, EarthSatellite, wgs84
from skyfield.toposlib import GeographicPosition
import similaritymeasures

logging.basicConfig(level=logging.DEBUG)

# Constants
logger = logging.getLogger(__name__)
CURRENT_DIR: Path = Path(__file__).parent
PROJECT_DIR: Path = CURRENT_DIR.parent.parent
REPLAY_DIR: Path = CURRENT_DIR.parent / "astro_pi_replay" / "resources"/ "replay"
KKKM_DIR: Path = REPLAY_DIR / "VIS" / "kkkm"
ts = load.timescale()
Latitude = float
Longitude = float
Id = str
Trajectory = list[tuple[Id, Latitude, Longitude, datetime]]
TRAJECTORIES_FILE: Path = CURRENT_DIR / "trajectories.csv"

### Helper functions ###
def utc_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str).replace(tzinfo=timezone.utc)

def decimal_to_time(dec: float) -> time:
    if not 0 <= dec < 1:
        raise ValueError("Input must be between 0 and 1")
    
    total_micros = dec * 24 * 60 * 60 * 1000000
    hours, remainder = divmod(total_micros, 3600 * 1000000)
    minutes, remainder = divmod(remainder, 60 * 1000000)
    seconds, microseconds = divmod(remainder, 1000000)

    return time(hour=int(hours), minute=int(minutes), 
                second=int(seconds), microsecond=math.floor(microseconds),
                tzinfo=timezone.utc)

def find_nearest_tle(start: datetime, end: datetime):
    master_tle_file = REPLAY_DIR.parent / "iss.txt"
    with master_tle_file.open() as f:
        lines = f.readlines()
    if len(lines) % 2 != 0:
        raise ValueError("Should have an even number of lines")
    tles: dict[datetime, list[list[str]]] = {}

    # group into sets of two lines
    for i in range(len(lines) // 2):
        tle = lines[i*2:i*2+2]
        fst,_ = tle
        # extract the epoch from the first line
        epoch: str = re.split(r"\s+", fst)[3]
        # the epoch is comprised of YY concatenated to tm_yday concatenated to time as decimal between 0 and 1.
        epoch_year: str = epoch[:2]
        year_start: str = "19" \
                if int(epoch_year) > int(str(datetime.now().year)[-2:]) else "20"
        year: int= int(year_start + epoch_year)
        yday: int = int(epoch[2:5])
        time = decimal_to_time(float(f".{epoch.split('.')[1]}"))
        dt = datetime(
            year, 1, 1, 
            time.hour, time.minute, time.second, time.microsecond,
            tzinfo=timezone.utc
        ) + timedelta(days=yday - 1)
        tles[dt] = [tle]

    df = pd.DataFrame.from_dict(tles, orient="index", columns=["tle"])
    df.sort_index(inplace=True)

    min_datetime = cast(pd.Timestamp, df.index[0]).to_pydatetime()
    max_datetime = cast(pd.Timestamp, df.index[-1]).to_pydatetime()

    mid_time: datetime = start + \
        timedelta(seconds=round((end - start).total_seconds() / 2))

    if mid_time < min_datetime or mid_time > max_datetime:
        raise ValueError("Mid point of start and end is outside the boundaries")

    nearest_i = df.index.get_indexer(pd.Index([mid_time]), method="backfill")[
        0
    ]

    line1, line2 = df.iloc[nearest_i]["tle"]
    return EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)

def build_trajectory(id: Id, start: datetime, end: datetime, iss: EarthSatellite) \
        -> list[tuple[Id, float, float, datetime]]:
    trajectory = []
    for i in range(int((end - start).total_seconds())):
        dt: datetime = start + timedelta(seconds=i)
        t: Time = ts.from_datetime(dt)
        pos: Geocentric = cast(Geocentric, iss.at(t))
        gps_pos: GeographicPosition = wgs84.subpoint(pos)
        lat = gps_pos.latitude.degrees
        lon = gps_pos.longitude.degrees
        trajectory.append((id, lat,lon, dt))
    return trajectory


def build_trajectory_dataframe() -> pd.DataFrame:
    trajectories: dict[str, Union[Trajectory,pd.DataFrame]] = {}
    COLUMNS: list[str] = ["id", "lat", "long", "name"]

    # Fetch the flight path we are matching to (kkkm), and the
    # appropriate TLE file:
    logger.debug("Fetching kkkm (trajectory to match to)")
    kkkm_metadata = KKKM_DIR / "metadata.json"
    with kkkm_metadata.open() as f:
        kkkm_metadata = json.load(f)
    kkkm_start: datetime = utc_datetime(kkkm_metadata["start"])
    kkkm_end: datetime = utc_datetime(kkkm_metadata["end"])
    kkkm_duration: int = round((kkkm_end - kkkm_start).total_seconds())
    kkkm_iss: EarthSatellite = find_nearest_tle(kkkm_start, kkkm_end)
    kkkm_trajectory: Trajectory = build_trajectory("kkkm", kkkm_start, kkkm_end, kkkm_iss)
    logger.debug("Built trajectory for kkkm")
    trajectories["kkkm"] = kkkm_trajectory
    
    # 2022
    logger.debug("Building 2022 trajectories...")
    with (PROJECT_DIR / "msl_2022.csv").open() as f:
        for line in f.readlines():
            logger.debug(f"line: {line}")
            split_line = line.split(",")
            logger.debug(f"split_line: {split_line}")
            try:
                name,start,end,_ = split_line
            except ValueError:
                pass
            name,start,end = split_line
            start = utc_datetime(start.strip())
            end = utc_datetime(end.strip())
            if round((end - start).total_seconds()) < kkkm_duration:
                # skip
                continue

            # create 10 minute 'windows' to compare
            window_final = end - timedelta(seconds=kkkm_duration)
            tick: int = 60 * 10 # every 30 minutes
            for i in range(0, round((window_final - start).total_seconds()), tick):
                window_start = start + timedelta(seconds=i)
                window_end = window_start + timedelta(seconds=kkkm_duration)
            
                logger.debug(f"Building trajectory for team {name} id {i}")
                trajectory = build_trajectory(str(i),
                    window_start, window_end, find_nearest_tle(window_start, window_end))
                trajectories[name] = trajectory

    # 2024
    for file in [
        "msl_2024-04-26_run1.csv", 
        "msl_2024-04-30_run2.csv",
        "msl_2024-05-06_run3.csv"]:
        to_open = PROJECT_DIR / file
        logger.info(to_open)
        with to_open.open() as f:
            run_id: str = file.split("_")[2].split(".")[0]
            for line in f.readlines():
                if line.startswith("rpf_data_collector"):
                    split_line = line.split(",")
                    name = split_line[0] + "_" + run_id
                    range_start = utc_datetime(split_line[1].strip())
                    range_end = utc_datetime(split_line[2].strip())
                    iss = find_nearest_tle(range_start, range_end)
                    trajectory: Trajectory = build_trajectory(name, range_start, range_end, iss)
                    trajectories[name] = trajectory

    dfs = []
    for name, traj in trajectories.items():
        df = pd.DataFrame(traj, columns=COLUMNS)
        df["name"] = name
        dfs.append(df)
    return pd.concat(dfs)

# trajectories = build_trajectory_dataframe()
if not TRAJECTORIES_FILE.exists():
    logger.info(f"File {TRAJECTORIES_FILE.name} not found - building...")
    df = build_trajectory_dataframe()
    df.to_csv(TRAJECTORIES_FILE, index=False)
    df = df.set_index("name")
else:
    df = pd.read_csv(TRAJECTORIES_FILE)
    df = df.set_index("name")


kkkm_traj: np.ndarray = df.loc["kkkm"][["lat", "long"]].to_numpy()

pcms = []
for i in df.groupby(["name", "id"]):
    name, subdf = i
    if "kkkm" in str(name):
        continue
    to_compare: np.ndarray = subdf[["lat", "long"]].to_numpy()
    pcm = similaritymeasures.pcm(kkkm_traj, to_compare)
    pcms.append((pcm, name))

pcms = sorted(pcms, key=lambda x: x[0])
print(pcms[:20])

# As a result of this, 'rpf_data_collector5_run2' was chosen as the closest match.
# We simply need to re-index it.
