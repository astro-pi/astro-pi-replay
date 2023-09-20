"""
Code based on
https://projects.raspberrypi.org/en/projects/astropi-iss-speed/8
"""

import logging
import os
from pathlib import Path
import time

from picamera import PiCamera
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

logger.debug("Before cam instantiated")
cam = PiCamera()
logger.debug("After cam instantiated")

photos = []
for i in range(2):
    photo_name: str = f"photo_{i+1}.jpg"
    print(os.listdir())
    print(os.getcwd())
    if not Path(photo_name).exists():
        print(f"Capturing {photo_name}")
        cam.capture(photo_name)
    photos.append(photo_name)

after = time.perf_counter()

logger.info("Captured images, calculating matches")
time_difference = get_time_difference(
    photos[0], photos[1]
)  # Get time difference between images
logger.info(f"time_difference: {time_difference}")
image_1_cv, image_2_cv = convert_to_cv(
    photos[0], photos[1]
)  # Create OpenCV image objects
keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(
    image_1_cv, image_2_cv, 1000
)  # Get keypoints and descriptors
matches = calculate_matches(descriptors_1, descriptors_2)  # Match descriptors
# display_matches(image_1_cv, keypoints_1, image_2_cv,
#                  keypoints_2, matches) # Display matches
coordinates_1, coordinates_2 = find_matching_coordinates(
    keypoints_1, keypoints_2, matches
)
average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
# speed = calculate_speed_in_kmps(average_feature_distance, 12648, time_difference)
speed = calculate_speed_in_kmps(average_feature_distance, 39588, time_difference)
after = time.perf_counter()
print(f"{speed:.2f} km/s")
profiler.stop()

profiler.print()
with open("report.html", "w") as f:
    f.write(profiler.output_html())
