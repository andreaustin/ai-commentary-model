# from jsonpath_ng import jsonpath, parse
# import nba_api.stats.endpoints as nba
# from attr import has

from pytube import YouTube
from datetime import date, timedelta
import os
from pprint import pprint
import json
import subprocess
import pandas
import requests
import numpy
import cv2
import streamlit as st

# Define constants for API endpoint handling
TODAY=date.today().strftime("%Y%m%d")
YESTERDAY=(date.today()-timedelta(days=1)).strftime("%Y%m%d")
sports_selection = {
    "nba": "basketball/nba",
    "nfl": "football/nfl"
}
BASE_URL=f"https://site.api.espn.com/apis/site/v2/sports"

class GameData:
    def __init__(self, league, date=TODAY):
        self.league = league
        self.date = date
        self.url = f"{BASE_URL}/{sports_selection[league]}"
        self.games = []
        self.highlights = []

    # GET endpoint handling functions
    def generate_base_url(league):
        if league not in sports_selection:
            raise ValueError(f"Unsupported league: {league}")
        return f"{BASE_URL}/{sports_selection[league]}"

    def games_list_url(self, date):
        return f"{self.url}/scoreboard?dates={date}"

    def game_info_url(self, event_id="401809963"):
        return f"{self.url}/summary?event={event_id}"

    def get_highlights(self, event_id="401809963"):
        url = f"{self.url}/summary?event={event_id}"
        event_data = requests.get(url).json()
        highlights = []
        for video in event_data['videos']:
            highlights.append({
                "videoID": video['id'],
                "title": video['headline'],
                "link": video['links']['web']['href'],
            })
        self.highlights = highlights
        return self.highlights

    def get_games(self):
        response = requests.get(self.games_list_url(self.date)).json()
        events = response["events"]
        for event in events:
            competitors = event.get("competitions", [{}])[0].get("competitors", [])
            homeScore = competitors[0]['score']
            awayScore = competitors[1]['score']
            self.games.append({
                "event_id": event["id"],
                "gameScore": f"A {awayScore} - {homeScore} H",
                "game": event["name"],
                "status": event["status"]["type"]["description"],
                "link": event["links"][0]["href"]
            })
        return self.games

    # Data processing
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
