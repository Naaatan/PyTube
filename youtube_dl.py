#!/usr/bin/env python
# coding: utf-8

import glob
import time
import os
import re
import subprocess

from pytube import Playlist, YouTube
from tqdm import tqdm

# consts
MUSIC_DIR = os.path.join(os.getcwd(), "music")
VIDEO_DIR = os.path.join(os.getcwd(), "videos")
pbar = None

def download_video(url):
    """
    Download video from YouTube.

    Parameters
    ----------
    url : str
        YouTube video URL

    Returns
    ----------
    info : dict
        Downloaded video info.
    """
    print("Downloading {url}".format(url=url))

    yt = YouTube(url)
    yt.register_on_progress_callback(show_progress_bar)
    yt.register_on_complete_callback(complete_download)

    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    return (stream.download(VIDEO_DIR), stream.title)


def download_playlist(url):
    """
    Download playlist from YouTube.

    Parameters
    ----------
    url : str
        YouTube playlist URL

    Returns
    ----------
    info : dict
        Downloaded video info.
    """
    print("Downloading {url}".format(url=url))

    pl = Playlist(url)
    video_infos = {}
    for video in pl.videos:
        try:
            video.register_on_progress_callback(show_progress_bar)
            video.register_on_complete_callback(complete_download)

            stream = video.streams.filter(progressive=True, file_extension='mp4').first()
            video_path = stream.download(VIDEO_DIR)
            video_infos[video_path] = stream.title
        except Exception as e:
            print(e)
            continue

    return video_infos


def is_playlist(video_url) -> bool :
    pattern_playlist = r'^(https|http)://www.youtube.com/playlist\?list=\.*'
    match = re.search(pattern_playlist, video_url)

    return True if match is not None else False


def convertMP3(video_path, title):
    if video_path:
        music_path = os.path.join(MUSIC_DIR, "{title}.mp3".format(title=title))
        subprocess.call([
            'ffmpeg',
            '-i',
            video_path,
            '-loglevel',    # 標準出力設定
            'error',        # エラーすべて
            # '-progress',    # 進捗表示
            # '-',            # 進捗を標準出力
            music_path
        ])
        return music_path
    return None


def show_progress_bar(stream, chunk, bytes_remaining):
    global pbar

    if pbar is None:
        print(stream.default_filename)
        pbar = tqdm(total=stream.filesize)

    progress = stream.filesize - bytes_remaining
    pbar.update(progress)
    time.sleep(0.01)


def complete_download(stream, file_path):
    global pbar
    
    if pbar is not None:
        pbar.close()
        pbar = None


def download_with_convert(url):
    if is_playlist(url):
        video_infos = download_playlist(url)
        for video_path, title in video_infos.items():
            music_path = convertMP3(video_path, title)
            convert_result_print(video_path, music_path)
    else:
        video_path, title = download_video(url)
        music_path = convertMP3(video_path, title)
        convert_result_print(video_path, music_path)


def convert_result_print(video_path, music_path):
    print()
    print("================== Result ==================")
    if video_path and music_path:
        print("video_path={video}".format(video=video_path))
        print("music_path={music}".format(music=music_path))
    elif video_path and (music_path is None):
        print("video_path={video}".format(video=video_path))
        print("music mp3 Convert Failed..")
    else:
        print("Download Failed")
    print("============================================")  


if __name__ == "__main__":
    print("Please input youtube video URL or playlist URL")
    print()
    url = input(">> ")
    download_with_convert(url)
