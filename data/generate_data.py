from datetime import date, timedelta
import os
from pprint import pprint
import json
import subprocess
from attr import has
import pandas
import requests
# from jsonpath_ng import jsonpath, parse
from pytube import YouTube
import numpy
import cv2
import nba_api.stats.endpoints as nba

TODAY=date.today().strftime("%Y%m%d")
YESTERDAY=(date.today()-timedelta(days=1)).strftime("%Y%m%d")
SPORT=input("What sports league would you like to check on?\n").lower().strip()
sports_selection = {
    "nba": "basketball/nba",
    "nfl": "football/nfl"
}
if SPORT in sports_selection:
    SPORT = sports_selection[SPORT]
BASE_URL=f"https://site.api.espn.com/apis/site/v2/sports/{SPORT}"
DATE=input("Which day did this/these event(s) occur?: (YYYYMMDD)\n(No input will default to yesterday)\n")
if not DATE:
    DATE=YESTERDAY

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

def get_yesterdays_games():
    return get_games(YESTERDAY)

def get_todays_games():
    return get_games(TODAY)

def games_list_url(date):
    return f"{BASE_URL}/scoreboard?dates={date}"

def game_info_url(event_id="401809963"):
    return f"{BASE_URL}/summary?event={event_id}"

def get_highlights(event_id="401809963"):
    url = f"{BASE_URL}/summary?event={event_id}"
    event_data = requests.get(url).json()
    highlights = []
    for video in event_data['videos']:
        highlights.append({
            "videoID": video['id'],
            "title": video['headline'],
            "link": video['links']['web']['href'],
        })
    return highlights

def get_games():
    games = []
    response = requests.get(games_list_url(DATE)).json()
    score = ""
    events = response["events"]
    for event in events:
        competitors = event.get("competitions", [{}])[0].get("competitors", [])
        homeScore = competitors[0]['score']
        awayScore = competitors[1]['score']
        games.append({
            "event_id": event["id"],
            "gameScore": f"A {awayScore} - {homeScore} H",
            "game": event["name"],
            "status": event["status"]["type"]["description"],
            "link": event["links"][0]["href"]
        })
    return games


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
    pprint(get_games())
    # pprint(get_highlights())
    # load_csv('data/sports_clips.csv')

if __name__ == "__main__":
    main()
