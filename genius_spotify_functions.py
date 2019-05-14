
import lyricsgenius
import requests
import math
import time
import re
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys

sleep_time = 3

genius = lyricsgenius.Genius("UzI86AWL4bI0YZ0f3nX5MAjFBKwoeivRrzaQS6N_NPRBsn8Eqoh2Vqe1JmQSddmA")

def referent_request(song_id, page):

    '''
    Given song id and name, returns 
    '''

    access_token = 'TfzHINvVahhaktHEu527mgWtUYCksCKLoqeecXkDaw61VDmsd85WstrxVdSmb1Dl'
    url = 'https://api.genius.com/referents?'
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url_params = {  'song_id': song_id,
                    'text_format': 'plain',
                    'page': page
                }
    response = requests.get(url, headers=headers, params=url_params, timeout=30)
    return response.json()['response']['referents']


def get_annotations(song_ids):
    all_annotations = {}

    for element in song_ids:
        # get annotation count for a given song
        annotation_count = element['annotation_count']

        # calculate number of pages of annotations for song
        pages = math.ceil(annotation_count/10)

        annotations = []
        print(element)
        
        # return referent info for all pages
        for x in list(range(1,pages+1)):
            full_referent = referent_request(song_id=element['song_id'],page=x)
            time.sleep(sleep_time)

            # get all annotations on given page
            for x in list(range(0,len(full_referent))):
                annotations.append(full_referent[x]['annotations'][0]['body']['plain'])

        # add song id and corresponding annotations to dictionary
        all_annotations[element['song_id']] = annotations
        
    return all_annotations

def song_name_to_id(song_queries):
    '''
    Given list of song queries with song name and artist, returns a list of dictionaries
    where each element contains a song id and the corresponding number of annotations.
    '''
    id_and_annotation_count = []

    for i, query in enumerate(song_queries):
        print(f'{i} {query}')
        result = genius.search_genius(query)['hits']
        time.sleep(sleep_time)
        if len(result) == 0:
            continue
        elif result[0]['result']['annotation_count'] < 3:
            continue
        else:
            id_and_annotation_count.append({'song_id': result[0]['result']['id'], 
                                            'annotation_count': result[0]['result']['annotation_count']})
        
    return id_and_annotation_count


client_id =  '4331599034204c14b995e8820cafedfe'
secret = '7de02824a1424b8ca06ebff037e38e00'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                      client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def playlist_ids(user):
    playlists = sp.user_playlists(user)
    playlist_ids = []
    while playlists:
        for playlist in playlists['items']:
            playlist_ids.append(playlist['id'])
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return playlist_ids


def get_playlist_tracks(playlist_ids):
    '''
    Returns list of lists where each element is a list of track_name + artist for each 
    song in the playlist.
    '''
    all_tracks = []
    for pl_id in playlist_ids:

        results = sp.user_playlist_tracks(user='Spotify', playlist_id=pl_id)
        tracks = results['items']

        # get all paginated tracks and artists from playlist
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        track_artist = []
        print(pl_id)
        for x in tracks:
            if x['track'] is not None:
                track_artist.append(x['track']['name'] + ' ' + x['track']['artists'][0]['name'])
            else:
                continue
            
        all_tracks.append(track_artist)
    return all_tracks



