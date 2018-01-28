import sys
import os
import json
import spotipy
import spotipy.util as util
import pandas as pd


def get_user_playlist(username, sp):
    #gets user playlist
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            print("Name: {}, Number of songs: {}, Playlist ID: {} ".format(playlist['name'].encode('utf8'),
                     playlist['tracks']['total'],
                     playlist['id']))

def get_playlist_content(username, playlist_id, sp):
    offset = 0
    songs = []
    while True:
        content = sp.user_playlist_tracks(username, playlist_id, fields=None,
                                          limit=100, offset=offset, market=None)
        songs += content['items']
        if content['next'] is not None:
            offset += 100
        else:
            break

    with open('{}-{}'.format(username, playlist_id), 'w') as outfile:
        json.dump(songs, outfile)

def get_audio_features(username, playlist_id, sp):
    offset = 0
    songs = []
    items = []
    ids = []
    while True:
        content = sp.user_playlist_tracks(username, playlist_id, fields=None,
                                          limit=100, offset=offset, market=None)
        songs += content['items']
        if content['next'] is not None:
            offset += 100
        else:
            break

    for song in songs:
        ids.append(song['track']['id'])

    index = 0
    audio_features = []

    while index < len(ids):
        audio_features += sp.audio_features(ids[index:index + 50])
        index += 50

    feature_list = []
    for features in audio_features:
        feature_list.append([features['energy'], features['liveness'],
                              features['tempo'], features['speechiness'],
                              features['acousticness'], features['instrumentalness'],
                              features['time_signature'], features['danceability'],
                              features['key'], features['duration_ms'],
                              features['loudness'], features['valence'],
                              features['mode'], features['type'],
                              features['uri']])

    df = pd.DataFrame(feature_list, columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'time_signature', 'danceability',
                                              'key', 'duration_ms', 'loudness',
                                              'valence', 'mode', 'type', 'uri'])

    df.to_csv('{}-{}.csv'.format(username, playlist_id), index=False)





if __name__ == '__main__':
    if len(sys.argv) > 1:
        #if the arguments in the list are greater than one
        username = sys.argv[1]
        print(username)

        #the username is the second argument
    else:
         #else no arguments given
        print("Whoops, need your username!")
        print("usage: python getdata.py [username]")
        sys.exit()


    token = util.prompt_for_user_token(username)

    if token:
        #if token is authorized
        sp = spotipy.Spotify(auth=token)
        #calls spotify client
        get_user_playlist(username, sp)
        #calls get_user_playlist
        playlist_id = raw_input(str("Input playlist id => ")) #input playlist id
        get_playlist_content(username, playlist_id, sp)
        get_audio_features(username, playlist_id, sp)




    else:
        print("Can't get token for", username)



