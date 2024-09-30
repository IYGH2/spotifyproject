from django.shortcuts import render # type: ignore
from django.http import JsonResponse # type: ignore
from django.http import HttpResponse # type: ignore
from django.conf import settings # type: ignore
from google.cloud import language_v2
import os
import spotipy # type: ignore
from spotipy import Spotify # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials # type: ignore
import numpy as np # type: ignore

def home(request):
    return render(request, 'home.html')

# フォームに入力されたテキストの感情分析を行う関数
def analyze_sentiment(text_content: str) -> dict:
    """テキストの感情を分析し、結果を返す関数"""
    client = language_v2.LanguageServiceClient()

    document_type_in_plain_text = language_v2.Document.Type.PLAIN_TEXT
    language_code = 'ja'

    document = {
        'content': text_content,
        'type_': document_type_in_plain_text,
        'language_code': language_code,
    }

    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={'document': document, 'encoding_type': encoding_type}
    )

    return response.document_sentiment.score

# 感情スコアとプレイリストのenergy属性の差を計算し、最小値のenergy属性の数値を返す
def get_nearest_value(energy_list, num):
    idx = np.abs(np.asarray(energy_list) - num).argmin()
    return energy_list[idx]

def reply(input):
    try:
        # クライアントIDとクライアントシークレットを設定
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET

        # 認証情報を設定
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = Spotify(client_credentials_manager=client_credentials_manager)

        # Spotifyプレイリストの選択
        playlist_id = '6KfKvkN7YEUFTwJHkczxdb'
        results = sp.playlist_tracks(playlist_id)

        if not results['items']:
            return HttpResponse('<h2>プレイリストが空です。</h2>', status=400)
    
        # プレイリスト内の全トラックIDを取得
        track_ids = [track['track']['id'] for track in results['items']]

        # 一度にまとめてトラックのaudio_featuresを取得
        audio_features = sp.audio_features(track_ids)

        track_info = []

        for track, audio_feature in zip(results['items'], audio_features):
            if audio_feature:
                song_energy = audio_feature['energy']
                track_info.append({
                    'name': track['track']['name'],
                    'artist': track['track']['artists'][0]['name'],
                    'url': track['track']['external_urls']['spotify'],
                    'energy': song_energy
                })

        # 感情スコアに最も近いenergy属性を見つける
        nearest_energy = get_nearest_value([track['energy'] for track in track_info], float(input))

        # レコメンド楽曲情報を取得
        recommended_music = next(track for track in track_info if track['energy'] == nearest_energy)

        return recommended_music
    
    except spotipy.exceptions.SpotifyException as e:
        print(f'Spotify APIエラー: {e}')
        return HttpResponse('<h2>Spotify APIに問題が発生しました。</h2>', status=500)

def bot_response(request):
    if request.method == 'POST':
        input_text = request.POST.get('input_text')

        # 入力されたテキストが空かどうかチェック
        if not input_text or input_text.strip() == "":
            return HttpResponse('<h2>テキストが入力されていません。</h2>', status=400)
    
        # 感情分析を実行
        sentiment_result = analyze_sentiment(input_text)

        # 感情スコアを元にSpotifyからレコメンド取得
        recommend_result = reply(sentiment_result)

        # JSON形式に変換
        response_data = {
            'recommend_music': recommend_result['name'],
            'recommend_artist': recommend_result['artist'],
            'recommend_url': recommend_result['url']
        }

        return JsonResponse(response_data, safe=False)
    else:
        return HttpResponse('<h2>からのデータを受け取りました。</h2>', status=400)

