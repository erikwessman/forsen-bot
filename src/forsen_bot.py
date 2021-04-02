import time
from datetime import datetime
import twitch_api
import twitter_api
import run_timer
import webhook
import json
from threading import Timer
import streamlink
from flask import Flask, request, Response


app = Flask(__name__)

def main():
    """
    Main method of the program, used to subscribe to webhook and make sure that everything is started properly
    """

    print('Starting bot...')
    
    webhook.sub_webhook('subscribe')
    print('Subscribed to webhook')

    if forsenbot.bot_active:
        print('Forsen is already online and playing Minecraft, starting checks in 20s...')
    else:
        print('Forsen is either not online or not playing Minecraft, waiting for notification...')

    print('Bot has started!\n')


@app.route('/my_webhook', methods=['GET', 'POST'])
def my_webhook():
    """
    Receives GET and POST requests
    GET requests are sent by Twitch when subscribing/unsubscribing, send back hub.challenge to confirm
    POST requests are sent by Twitch when an event occurs, for example when forsen starts the stream
    When we get POST request we change the bot_active boolean to be the appropriate type
    """

    if request.method == 'GET':
        return request.values.get('hub.challenge')

    elif request.method == 'POST':
        if webhook.validate_request(request):
            data = request.get_json()['data']
            if data:
                data = data[0]
                if data['game_name'] == 'Minecraft':
                    print('Stream changed: Forsen is playing Minecraft, stream is active.')
                    forsenbot.set_bot_active(True)
                else:
                    print('Stream changed: Forsen is NOT playing Minecraft, stream is not active.')
                    forsenbot.set_bot_active(False)
            else:
                print('Stream changed: Forsen is offline.')
                forsenbot.set_bot_active(False)

    return Response(status=200)


def stream_check():
    """
    If the stream is active, takes a screenshot of the speedrun timer
    If the timer is above the threshold (15 minutes) and a run isn't ongoing, tweet
    """

    if forsenbot.bot_active:
        print('Checking stream at', datetime.now())

        #Returns a boolean, True if we managed to take screenshot
        took_screenshot = twitch_api.take_screenshot(forsenbot.stream)

        timer = run_timer.get_timer('screenshots/capture.png')

        if timer and took_screenshot:
            print('Timer is at {} minutes and {} seconds'.format(timer[0], timer[1]))

            #Timer passed 15 min
            if run_timer.time_passed(timer, forsenbot.timer_threshold):
                check_make_tweet()

        else:
            print('Either unable to detect timer or unable to take screenshot')

        print('Completed check, waiting 20s... \n')


def check_make_tweet():
    """
    Checks if we should post any tweets
    """

    #A run above 15 min is not already ongoing, post normal tweet
    if not run_timer.run_ongoing(forsenbot.previous_time, time.time()):
        twitter_api.post_tweet()
        forsenbot.previous_time = time.time()

    #On the Ender dragon fight
    if run_timer.check_dragon('screenshots/capture.png'):

        #Forsen is in the End, and a dragon fight is not already ongoing, post special tweet
        if not run_timer.run_ongoing(forsenbot.previous_dragon_time, time.time()):
            twitter_api.post_dragon_tweet()
            forsenbot.previous_dragon_time = time.time()


class ForsenBot():
    """
    Class that contains information about the bot and Streamlink
    Contains an instance of RepeatedTimer that is started and stopped
    when the stream is active/inactive
    """

    def __init__(self, stream_url, stream_quality, timer_threshold, previous_time, previous_dragon_time):
        self.stream_url = stream_url
        self.stream_quality = stream_quality
        self.timer_threshold = timer_threshold
        self.previous_time = previous_time
        self.previous_dragon_time = previous_dragon_time

        self.bot_active = False
        self.repeated_timer = None
        self.streams = {}
        self.stream = None

    def set_bot_active(self, bot_active):
        self.bot_active = bot_active

        #An instance of the repeated timer already exists, terminate it
        if self.repeated_timer:
            self.repeated_timer.stop()

        if bot_active:
            self.streams = streamlink.streams(self.stream_url)
            self.stream = self.streams[self.stream_quality].url

            self.repeated_timer = RepeatedTimer(20, stream_check)
            self.repeated_timer.start()

            print('Starting stream checks...')
            print('The first check might fail because of the Twitch purple screen of death')

        else:
            self.streams = {}
            self.stream = None


class RepeatedTimer(object):
    """
    Calls a function in intervals, runs on a separate thread to be non-blocking
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


forsenbot = ForsenBot('https://www.twitch.tv/forsen', '720p60', [15,0], 0, 0)
forsenbot.set_bot_active(twitch_api.is_playing_minecraft())
main()