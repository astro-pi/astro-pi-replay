import math


def calc_gsd(
    sensor_size: tuple[float, float],
    focal_length: int,
    altitude: int,
    resolution: tuple[float, float],
) -> tuple[float, float]:
    ground_distances = []
    for sensor_dim in sensor_size:
        angle = math.atan2(sensor_dim / 2, focal_length)
        ground_distance = 2 * altitude * math.tan(angle)
        ground_distances.append(ground_distance)
    return tuple(ground_distances)
