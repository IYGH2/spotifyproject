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

    if request.method == 'POST':
        input_text = request.POST.get('input_text')

        # Spotify APIで楽曲を検索
        results = sp.search(q='track'+input_text, limit=1, offset=0, type='track', market='JP')

        # 最初のトラックを取得
        track = results['tracks']['items'][0]

        # アーティスト名、楽曲名、URLを一度に取得
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        track_url = track['external_urls']['spotify']

        # JSON形式に変換
        response_data = {'name': track_name,
                         'artist': artist_name,
                         'url': track_url
                        }

    return JsonResponse(response_data, safe=False)

