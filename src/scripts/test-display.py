import datetime
import json
import logging
import re
import subprocess
import tkinter as tk

import numpy as np
from PIL import Image, ImageTk

from astro_pi_executor.resources import get_resource

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

VIDEO_FILE = str((get_resource("OrbitAz") / "OrbitAz.mp4").resolve())


class Preview:
    def fetch_metadata(self, file: str) -> tuple[int, int, float]:
        """Fetches the width, height, and framerate"""
        out = subprocess.run(  # nosec B603, B607
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", file],
            check=True,
            capture_output=True,
        )
        metadata = json.loads(out.stdout)["streams"][0]
        quotient = re.findall("\\d+", metadata["avg_frame_rate"])

        if len(quotient) != 2:
            raise Exception("Cannot read framerate " + f"from {self.file}")
        logging.debug(f"quotient: {quotient}")
        framerate: float = int(quotient[0]) / int(quotient[1])
        return int(metadata["width"]), int(metadata["height"]), framerate

    def __init__(self, file: str):
        self.file = file
        width, height, framerate = self.fetch_metadata(file)
        self.width = width
        self.height = height
        self.framerate = framerate

    def run(self) -> None:
        """Start the output stream. Frames are outputted as fast
        as possioble to the pipe as the -re option introduced a
        significant delay at the beginning of the stream. The
        receiver must therefore read the input frames with the
        correct framerate"""
        command_args: list[str] = [
            "ffmpeg",
            "-loglevel",
            "quiet",
            "-i",
            self.file,
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-an",
            "-tune",
            "zerolatency",
            "pipe:",
        ]
        command: str = " ".join(command_args)
        logging.debug(command)
        self.proc = subprocess.Popen(command_args, stdout=subprocess.PIPE)  # nosec B603

        self.start_time: datetime.datetime = datetime.datetime.now()
        self.interval: int = round((1 / self.framerate) * 1000)
        logger.info(f"reading frames with interval: {self.interval}")

        self.window = tk.Tk()
        self.window.title("Astro Pi Executor")
        self.window.call(
            "wm",
            "iconphoto",
            self.window._w,  # type: ignore
            ImageTk.PhotoImage(file=str(get_resource("AstroPi_2021_colour.png"))),
        )
        self.label = tk.Label(self.window)
        self.label.grid()
        self.label.pack()
        self.label.after(self.interval, self.refresh)

    def refresh(self):
        if self.proc.stdout is not None:
            logging.debug(f"Reading {self.width*self.height*3} bytes from pipe...")
            frame_bytes = self.proc.stdout.read(self.width * self.height * 3)
            if frame_bytes:
                logger.debug("Created img")
                array = np.frombuffer(frame_bytes, np.uint8).reshape(
                    [self.height, self.width, 3]
                )
                img = Image.fromarray(array)
                imgtk = ImageTk.PhotoImage(image=img)
                logging.debug("Adding new image to window")
                self.label.configure(image=imgtk)
                self.label.image = imgtk
                self.label.after(self.interval, self.refresh)
        else:
            logger.warn("Proc.stdout is none")


if __name__ == "__main__":
    gui = None
    start_time = datetime.datetime.now()
    try:
        gui = Preview(VIDEO_FILE)
        gui.run()
        gui.window.mainloop()
    finally:
        if gui is not None and hasattr(gui, "proc"):
            gui.proc.terminate()
