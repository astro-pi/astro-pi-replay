from astro_pi_replay.resources import get_tle, get_replay_dir, get_replay_sequence_dir, get_metadata
from pathlib import Path
from typing import Any


def test_get_replay_dir():
    replay_dir: Path = get_replay_dir()
    assert replay_dir.name == "replay"

def test_get_replay_sequence_dir():
    sequence_dir: Path = get_replay_sequence_dir()
    assert sequence_dir.is_relative_to(get_replay_dir())
    assert get_replay_sequence_dir().name == "test_data"

def test_get_metadata():
    metadata: dict[str,Any] = get_metadata()
    expected_metadata: dict[str, Any] = {
        "altitude_average_km": 408,
        "camera": {
	        "name": "Sony IMX477",
	        "sensor_size_x": "6.287mm",
	        "sensor_size_y": "4.712mm",
	        "sensor_resolution_x": 4056,
	        "sensor_resolution_y": 3040
        },
        "lens": {
	        "name": "Kowa 5mm C-mount Lens",
	        "focal_length": "5mm"
        },
        "ground_sampling_distance_cm": 39588,
        "resolution_x": 1280,
        "resolution_y": 720,
        "tle": {
            "file": "data/iss-23097_09993082.tle",
            "sha256sum": "545c9581ca3d2bcd7d772a770ed7b70bfaa4613f1bd4d43530ff86a152afbe63"
        },
        "start": "2023-04-27 06:41:09.939574",
        "end": "2023-04-27 09:40:47.108350", 
        "team_credits": "OrbitAz",
        "photography_type": "VIS",
        "photos": {
            "prefix": "img",
	        "suffix": "jpg",
	        "isZeroIndexed": True
        },
        "video": "OrbitAz.mp4"
    }
    assert metadata == expected_metadata


def test_get_tle():
    tle_file: Path = get_tle()
    sequence_dir: Path = get_replay_sequence_dir()
    tle_metadata: dict[str,str] = get_metadata("tle")
    assert tle_file.is_relative_to(sequence_dir)
    assert str(tle_file.relative_to(sequence_dir)) == tle_metadata["file"]

