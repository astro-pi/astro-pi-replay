from picamzero import Camera
from pathlib import Path

current_dir = Path(__file__).parent

cam = Camera()
cam.add_image_overlay(current_dir / "rocket.png")
cam.take_photo("basic_photo_with_overlay.jpg")
