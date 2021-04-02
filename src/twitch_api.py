import requests
import cv2
import time
from time import sleep
from os import environ


#Authorize Twitch api client
client_id = environ.get('twitch_client_id')
client_secret = environ.get('twitch_client_secret')

url = 'https://api.twitch.tv/helix/streams?user_login=forsen'

#Verify requests made to Twitch api
auth_url = 'https://id.twitch.tv/oauth2/token'
auth_params = {'client_id': client_id,
               'client_secret': client_secret,
               'grant_type': 'client_credentials'}


def get_stream_info():
    """
    Uses the Twitch API to get information about Forsens stream
    """

    auth_call = requests.post(url=auth_url, params=auth_params)
    access_token = auth_call.json()['access_token']

    header = {'Client-ID': client_id, 
              'Authorization' :  "Bearer " + access_token, 
              'Accept': 'application/vnd.twitchtv.v5+json'}

    r = requests.get(url, headers=header).json()['data']
    return r


def is_playing_minecraft():
    """
    Checks if Forsen is playing Minecraft using the get_stream_info() function
    """

    info = get_stream_info()
    if info:
        info = info[0]
        return info['game_name'] == 'Minecraft'
    return False


def take_screenshot(stream):
    """
    Uses OpenCV to take a screenshot of the stream from Streamlink
    """

    print('Taking screenshot...')

    cap = cv2.VideoCapture(stream)
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite('screenshots/capture.png', frame)

    return ret
