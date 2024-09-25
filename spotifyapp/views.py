from django.shortcuts import render
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from django.http import JsonResponse
from django.conf import settings
import time
from requests.exceptions import HTTPError


def home(request):
    return render(request, 'home.html')

def bot_response(request):
    # クライアントIDとシークレットを設定
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # プレイリストIDを指定
    playlist_id = '0s3tAQfErgfq0LuMZiGeKF'

    # プレイリストのトラックを取得
    results = sp.playlist(playlist_id)

    # 楽曲のタイトル、アーティスト名、IDをリストに格納する
    tracks_data = []

    for item in results['tracks']['items']:
        track = item['track']
        track_data = {
            'name': track['name'],
            'urls': track['external_urls']['spotify'],
            'artists': ', '.join([artist['name'] for artist in track['artists']])
        }
        tracks_data.append(track_data)

    # ランダムなインデックスを取得
    random_index = random.choice(range(len(tracks_data)))

    # ランダムなトラック情報を取得
    random_track = tracks_data[random_index]

    # JSON形式に変換
    response_data = {
    'name': random_track['name'],
    'urls': random_track['urls'],
    'artists': random_track['artists']
    }

    return JsonResponse(response_data, safe=False)

