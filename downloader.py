import os
import tempfile
import yt_dlp


def download_video(url):
    folder = tempfile.mkdtemp()

    output = os.path.join(
        folder,
        "%(title)s.%(ext)s"
    )

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output,
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename


def download_audio(url):
    folder = tempfile.mkdtemp()

    output = os.path.join(
        folder,
        "%(title)s.%(ext)s"
    )

    options = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename
