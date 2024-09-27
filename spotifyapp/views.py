from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from google.cloud import language_v2


def home(request):
    return render(request, 'home.html')

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

    return {
        'score': response.document_sentiment.score,
        'magnitude': response.document_sentiment.magnitude
    }


def bot_response(request):
    if request.method == 'POST':
        input_text = request.POST.get('input_text')

        # 感情分析を実行
        sentiment_result = analyze_sentiment(input_text)

        # JSON形式に変換
        response_data = {
            'sentiment_score': sentiment_result['score'],
            'sentiment_magnitude': sentiment_result['magnitude']
        }

    return JsonResponse(response_data, safe=False)

