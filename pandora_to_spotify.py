import json
import logging
import requests
import pprint
import time

# Configure logger.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the constants.
track_location = 'raw_pandora_tracks.txt'
o_auth = ''
base_url = 'https://api.spotify.com/v1/'

found_uris = []
tracks_not_found = []

# Connects to Spotify API.
try:
    s = requests.Session()
    s.verify = False
    s.stream = True
    s.trust_env = False

    s.headers.update({'Authorization': 'Bearer {}'.format(o_auth)})
    response = s.get(base_url)
    logger.debug('Response is: {}'.format(response.content))
except:
    raise

if(response.status_code == 400):

    # Opens the file and stores it as JSON.
    with open(track_location) as file:
        track_file = json.load(file)

    # Iterate over the tracks in the file to search on Spotify.
    for track in track_file['tracks']:
        url = base_url + 'search?q=track:{}%20artist:{}&type=track&limit=1'.format(track['track'], track['artist'])
        response = s.get(url)

        while response.status_code == 429:
            logger.debug('Status Code {}.  Sleeping for {}.'.format(response.status_code, response.headers['Retry-After']))
            time.sleep(int(response.headers['Retry-After']))
            response = s.get(url)

        if(response.status_code == 200):
            response = response.json()
            if len(response['tracks']['items']) > 0:
                logger.debug('Found - Artist: {} Track: {}'.format(track['artist'], track['track']))
                found_uris.append(response['tracks']['items'][0]['uri'])
            else:
                logger.debug('MISSED - Artist: {} Track: {}'.format(track['artist'], track['track']))
                tracks_not_found.append(track)


    pprint.pprint(found_uris)
    pprint.pprint(tracks_not_found)
