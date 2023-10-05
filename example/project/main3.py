"""
Code based on
https://projects.raspberrypi.org/en/projects/astropi-iss-speed/8
"""

import logging
import numpy as np
import os
from pathlib import Path
import shutil

from pyinstrument import Profiler
from iss_speed import (
    calculate_features,
    calculate_matches,
    calculate_mean_distance,
    calculate_speed_in_kmps,
    convert_to_cv,
    find_matching_coordinates,
    get_time_difference,
)


profiler = Profiler()
profiler.start()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sample_speed_in_kmps(image1, image2) -> float:
    time_difference = get_time_difference(
        image1, image2
    )  # Get time difference between images
    # can probably save time here by memoizing this
    image_1_cv, image_2_cv = convert_to_cv(
        image1, image2
    )  # Create OpenCV image objects
    keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(
        image_1_cv, image_2_cv, 1000
    )  # Get keypoints and descriptors
    matches = calculate_matches(descriptors_1, descriptors_2)  # Match descriptors
    coordinates_1, coordinates_2 = find_matching_coordinates(
        keypoints_1, keypoints_2, matches
    )
    average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
    speed = calculate_speed_in_kmps(
        average_feature_distance, 12648, time_difference
    )  # 4056x3040: 2.45kmps
    # # 2028x1520: 4.91kmps
    # speed = calculate_speed_in_kmps(average_feature_distance,
    #                                      25296.80, time_difference)
    # # 2028x1080: 6.91kmps
    # speed = calculate_speed_in_kmps(average_feature_distance,
    #                                      35601.78, time_difference)
    # # 1332x990: 7.53kmps
    # speed = calculate_speed_in_kmps(average_feature_distance,
    #                                      38838.30, time_difference)
    # 53402.67 # 1280x720

    return speed


def simple_moving_average(samples: list[float], k: int) -> float:
    """
    k: The window size
    """
    as_ndarray: np.ndarray = np.ndarray(samples[-k:])
    return np.sum(as_ndarray) / k


def weighted_moving_average(samples: list[float], n: int) -> float:
    as_ndarray: np.ndarray = np.ndarray(samples[-n:])
    denominator = n * (n + 1) / 2
    return (
        np.sum(np.multiply(as_ndarray, np.ndarray([n - i for i in range(n)])))
        / denominator
    )


def exponential_moving_average(samples: list[float]) -> float:
    logger.info(f"samples: {samples}")
    as_ndarray: np.ndarray = np.array(samples)
    logger.info(f"as_ndarray: {as_ndarray}")
    weights: np.ndarray = np.array(
        [np.e**-i for i in range(len(as_ndarray) - 1, -1, -1)]
    )
    logger.info(f"weights: {weights}")
    return np.average(as_ndarray, weights=weights)


photos_dir: Path = Path("../../src/astro_pi_replay/resources/replay/photos")
assert photos_dir.exists()

photos: list[str] = []
samples: list[float] = []

for i in range(30):
    photo_name: str = f"photo_{i+1}.jpg"
    if not Path(photo_name).exists():
        shutil.copy2(photos_dir / f"image{i+1}.jpg", photo_name)
        photos.append(photo_name)
    if len(photos) >= 2:
        sampled_speed_in_kmps = sample_speed_in_kmps(photos[-2], photos[-1])
        logger.debug(f"Sampled: {sample_speed_in_kmps}")
        samples.append(sampled_speed_in_kmps)
        current_average = exponential_moving_average(samples)
        logger.info(f"Current estimate: {current_average:.2f} km/s")

with open("samples.csv", "w") as f:
    f.write(os.linesep.join((str(sample) for sample in samples)))

profiler.stop()
profiler.print()
with open("report.html", "w") as f:
    f.write(profiler.output_html())
