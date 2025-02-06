import ffmpeg # ffmpeg-python

# todo test video from https://gist.github.com/jsturgis/3b19447b304616f18657
final_filename="image"
final_format="jpg"

ffmpeg.input(
    f'{final_filename}-%d.{final_format}', framerate=1
).output(
    f'{final_filename}.mp4', vcodec='libx264', pix_fmt='yuv420p'
).run(
    overwrite_output=True
)

