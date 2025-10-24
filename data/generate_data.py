import sh
import os
import subprocess
import pandas
from pytube import YouTube
import numpy
import cv2
import nba_api.stats.endpoints as nba

def segment_clips(url, start, end, label, title):
    outdir = "data/processed"
    os.makedirs(os.path.join(outdir, label))

    # Stream video to buffer to be trimmed with OpenCV
    video = YouTube(url).streams.filter(file_extension="mp4", only_video=True).first()
    buffer = video.stream_to_buffer()
    buffer.seek(0)
    
    tmp = os.path.join(outdir, f"tmp.mp4")
    with open(tmp, 'wb') as f:
        f.write(buffer.read())

    c = cv2.VideoCapture(tmp)

def get_nba_data():

def load_csv(dataset):
    df = pandas.read_csv(dataset)
    dataset = list(df.iterrows())

    # Parse clips
    for i, keys in dataset:
        segment_clips(
            url=keys["video_url"],
            start=keys["start_time"],
            end=keys["end_time"],
            label=keys["label"],
            title=f"{keys["label"]}_{i}",
        )

def main():
    subprocess.run("ls")
    load_csv('data/sports_clips.csv')

if __name__ == "__main__":
    main()
