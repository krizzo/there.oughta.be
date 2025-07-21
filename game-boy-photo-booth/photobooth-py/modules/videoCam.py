import ffmpeg
import os

def recordVideo(frames, out):
    print("Record video")
    return (
        ffmpeg.input("/dev/video0", f="v4l2", r=30, input_format="mjpeg", an=None)
              .output(out, vframes=frames+60, vcodec="copy", acodec="none")
              .overwrite_output()
              .run_async()
    )
