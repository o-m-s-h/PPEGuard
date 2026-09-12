"""Produce browser-compatible H.264 videos using a bundled FFmpeg binary."""
import subprocess

import imageio_ffmpeg


def encode_for_browser(source, destination):
    completed = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-y", "-i", str(source),
         "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(destination)],
        capture_output=True, text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Video encoding failed: {completed.stderr[-2000:]}")
    source.unlink()
