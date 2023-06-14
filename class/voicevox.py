import requests, json
import io
import wave
import time

import pyaudio

import player

"""
リファレンスURL
https://snuow.com/blog/%E3%80%90python%E3%80%91voicevox%E3%82%92python%E3%81%8B%E3%82%89%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95/
"""

class Voicevox:

    def __init__(self,charactor_id=0, host="127.0.0.1", port=50021, ):
        self.charactor_id = charactor_id
        self.host = host
        self.port = port

    def set_charactor(self, charactor_id:int):
        self.charactor_id = charactor_id

    def speak(self,text=None):

        params = (
            ("text", text),
            ("speaker", self.charactor_id)  # 音声の種類をInt型で指定
        )

        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )

        p = player.Player()
        p.play_wave(res.content)


def main():
    vv = Voicevox()
    vv.speak(text='こんにちは')


if __name__ == "__main__":
    main()

