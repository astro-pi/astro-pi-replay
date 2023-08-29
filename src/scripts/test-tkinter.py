import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from astro_pi_executor.resources import get_resource

window = tk.Tk()
window.title("Foo")
img = Image.open(get_resource(Path("replay") / "photos" / "image0.jpg"))
print(img)
img_tk = ImageTk.PhotoImage(image=img)
label = tk.Label(window, image=img_tk)
label.pack()
window.mainloop()
