import requests
import json

import config


def main():
    text = 'これはテスト用の音声ファイルです。'
    path = 'test.wav'

    params = {'text': text, 'speaker': config.voicevox_charactor_id}
    audio_query_response = requests.post('http://127.0.0.1:50021/audio_query', params=params).json()

    params = {'speaker': config.voicevox_charactor_id}
    headers = {'content-type': 'application/json'}
    audio_query_response_json = json.dumps(audio_query_response)

    res = requests.post(
        'http://127.0.0.1:50021/synthesis',
        data=audio_query_response_json,
        params=params,
        headers=headers
    )
    
    with open(path, 'wb') as f:
        f.write(res.content)


if __name__ == '__main__':
    main()