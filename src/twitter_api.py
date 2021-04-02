import tweepy
from os import environ
from random import choice

#Twitter API information
client_id = environ.get('twitter_client_id')
client_secret = environ.get('twitter_client_secret')
access_token = environ.get('twitter_access_token')
access_token_secret = environ.get('twitter_access_secret')

#Authorizes the instance of Tweepy
auth = tweepy.OAuthHandler(client_id, client_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
user = api.me()

tweet_list = ['Looks like Forsen is on a good run.',
              'Forsen is about to throw another god seed!',
              'TEH URN PagMan.',
              'Go long, Forsen is about to throw!',
              'Is this the one?',
              'This is the one Kap.',
              'This is not the one... Sadge']


def post_tweet():
    """
    Uses Tweepy to post tweet with a screenshot of the stream
    """
    
    api.update_with_media('screenshots/capture.png', choice(tweet_list) + ' Check out the stream: \nhttps://twitch.tv/forsen')
    print('posted tweet')


def post_dragon_tweet():
    """
    Uses Tweepy to post tweet about the dragon fight with a screenshot of the stream
    """

    api.update_with_media('screenshots/capture.png', 'Dragon fight! Check out the stream: \nhttps://twitch.tv/forsen')
    print('posted dragon tweet')
