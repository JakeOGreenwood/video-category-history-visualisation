import argparse
import requests
import pandas as pd
import re
import json

from bs4 import BeautifulSoup


class VideoTimeGraph:
    def __init__(self):
        self.api_key = "AIzaSyAj_BaZGoE8fGEaH2zBNkrqHnFVfU78ie8"
        self.youtube_api_url = "https://www.googleapis.com/youtube/v3/videos"

        print("initialised")

    def load_html(self, history_html):
        '''
        Unpacks raw video information into 2d listm stored in self.video_dataframe

        list of format:
        [channel_url,channel_name,video_url,video_title,utc]
        '''

        html_page = open(history_html)
        soup = BeautifulSoup(html_page, 'html.parser')

        video_section = soup.find_all(class_="mdl-cell--6-col")# Each video is kept in one of these classes

        invalid_links = []
        video_list = []


        for elem in video_section:
            # finds the two youtube links within the class, one channel link, one video
            links = elem.find_all('a', href=True)
            if len(links) != 2:
                # Videos not included- usually deleted, removed, or made private on youtube
                invalid_links.append(links)
            else:
                channel_url = links[1].get('href')
                channel_name = links[1].get_text()
                video_url = links[0].get('href')
                video_title = links[0].get_text()
                utc = elem.find(string=(re.compile("UTC")))

                video_list.append([channel_url,channel_name,video_url,video_title,utc])

                video_dataframe = {
                "channel_url":channel_url,
                "channel_name":channel_name,
                "video_url":video_url,
                "video_title":video_title,
                "utc":utc
                }
        self.video_dataframe = pd.DataFrame(video_list, columns=["channel_url","channel_name","video_url","video_title","utc"])
        #print(self.video_dataframe)
        #self.video_list = video_list

    def youtube_api_category_request(self, video_id_list=["Ks-_Mh1QhMc%2Cc0KYU2j0TM4%2CeIho2S0ZahI"]):
        '''
        Calls youtube data api v3 requesting data on videos in input list
        Takes list of video Ids - returns list of categories
        '''

        video_id_string = "?id=" +"&".join(video_id_list)

        # Video id cannot be entered into params due to percent encoding within the requests package. This is not configurable.
        # Instead video ID must be entered manually
        params = {"part": "snippet", "videoCategoryId": "string", "key": self.api_key}

        try:
            response = requests.get(self.youtube_api_url+video_id_string, params=params)
            print(response.url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            print("HTTP error occurred accesing youtube api: %s", http_error)
        except Exception as error:
            print("Other error occurred : ", error)

        # Json returned by api is converted to a dict and the category ID extracted.
        response_dict = response.json()

        # Details of other information available are in API documentation
        category_id_list = []
        for i in range(len(video_id_list)):
            category_id_list.append(response_dict["items"][i]["snippet"]["categoryId"])

        return category_id_list

    def run(self, history_html):
        self.load_html(history_html)
        print(self.video_list[:3])
        #self.youtube_api_category_request()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("history",type=str,help="Your Youtube watch history HTML file")
    parser.add_argument("api key",type=str,help="Your Youtube Data v3 API Key found on https://console.developers.google.com/apis/credentials")

    args = parser.parse_args()


    history_html = args.history

    video_time_graph = VideoTimeGraph()
    video_time_graph.run(history_html)
