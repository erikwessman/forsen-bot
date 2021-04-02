import requests
from hashlib import sha256
import hmac
from os import environ

#Used to verify client to twitch api
client_id = environ.get('twitch_client_id')
client_secret = environ.get('twitch_client_secret')

#Forsens twitch id
streamer_id = '22484632'

#Arbitrary secret that is used to verify payloads
payload_secret = environ.get('twitch_payload_secret')

#Authorizes requests made to Twitch api
auth_url = 'https://id.twitch.tv/oauth2/token'
auth_params = {'client_id': client_id,
               'client_secret': client_secret,
               'grant_type': 'client_credentials'}


def validate_request(post_request):
    """
    Receives a HTTP POST request and verifies it
    Request is signed with a sha256 hash of the payload secret and the payload contents
    Function generates hash using secret + payload and compares to signature
    """

    signature = post_request.headers.get('X-Hub-Signature').replace('sha256=', '')

    payload = post_request.get_data()

    computed_hash = hmac.new(payload_secret.encode(), msg=payload, digestmod=sha256).hexdigest()

    return signature == computed_hash


def sub_webhook(method_sub_unsub):
    """
    Sends request to Twitch API to subscribe to a webhook topic
    Twitch sends POST request to callback URL when event occurs
    A subscription lasts for 10 days
    """

    endpoint = 'https://api.twitch.tv/helix/webhooks/hub'
    topic = 'https://api.twitch.tv/helix/streams?user_id=' + streamer_id
    callback_url = environ.get('webhook_callback_url') + '/my_webhook'

    auth_call = requests.post(url=auth_url, params=auth_params)
    access_token = auth_call.json()['access_token']

    header = {'Client-ID': client_id, 
              'Authorization' :  "Bearer " + access_token, 
              'Accept': 'application/vnd.twitchtv.v5+json'}

    payload = {
        'hub.callback': callback_url,
        'hub.mode': method_sub_unsub,
        'hub.topic': topic,
        'hub.lease_seconds': 864000,
        'hub.secret': payload_secret}

    r = requests.post(endpoint, headers=header, json=payload)
    return r.ok


def get_subscriptions():
    """
    Uses Twitch API to fetch all the subscriptions associated with our application
    """

    endpoint = 'https://api.twitch.tv/helix/webhooks/subscriptions'

    auth_call = requests.post(url=auth_url, params=auth_params)
    access_token = auth_call.json()['access_token']

    header = {'Client-ID': client_id, 
              'Authorization' : "Bearer " + access_token, 
              'Accept': 'application/vnd.twitchtv.v5+json'}
    
    r = requests.get(endpoint, headers=header).json()
    return r
