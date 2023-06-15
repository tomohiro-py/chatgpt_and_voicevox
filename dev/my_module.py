import speech_recognition as sr
import pyttsx3
import openai
import dev.config as config
import requests
from time import sleep, perf_counter
import pyaudio
import wave
import io
import json
import logging

def test():
    print('test')

def speech_to_text():
    r = sr.Recognizer()
    r.pause_threshold = .8
    r.energy_threshold = 4000
    
    with sr.Microphone() as source:
        while True:
            try:
                print('start listening...')
                voice = r.listen(source)
                r.adjust_for_ambient_noise(source)

                print('recognizing...')
                text = r.recognize_google(voice, language="ja-JP")

                if text is not None:
                    break

            except Exception as e:
            # eが空っぽい。
                print("Waiting you 5s...")
                for i in reversed(range(1,6)):
                    print("{}s...".format(i), flush=False)
                    sleep(1)

    return text

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty("rate",200)
    engine.setProperty('volume',1.0)    # ボリュームは、0.0~1.0の間で設定します。

    words = text.split()
    for word in words:
        engine.say(word)

    engine.runAndWait()

def voicevox_text_to_speech(text: str):
    print('start voicevox process ...')
    content = voicevox_post_audio_query(text)
    binary = voicevox_post_synthesis(content)
    print('audio is ready ...')
    play_wavbytes(binary)

def voicevox_post_audio_query(text: str) -> dict:
    params = {'text': text, 'speaker': config.voicevox_charactor_id}
    res = requests.post('http://127.0.0.1:50021/audio_query', params=params)
    return res.json()

def voicevox_post_synthesis(audio_query_response: dict) -> bytes:
    params = {'speaker': config.voicevox_charactor_id}
    headers = {'content-type': 'application/json'}
    audio_query_response_json = json.dumps(audio_query_response)
    res = requests.post(
        'http://127.0.0.1:50021/synthesis',
        data=audio_query_response_json,
        params=params,
        headers=headers
    )
    return res.content

def play_wavbytes(wav_file: bytes):
    wr: wave.Wave_read = wave.open(io.BytesIO(wav_file))
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(wr.getsampwidth()),
        channels=wr.getnchannels(),
        rate=wr.getframerate(),
        output=True
    )
    chunk = 1024
    data = wr.readframes(chunk)
    while data:
        stream.write(data)
        data = wr.readframes(chunk)
    sleep(.5)
    stream.close()
    p.terminate()

def play_wavfile(wav_file: str):
    wr: wave.Wave_read = wave.open(wav_file, 'r')
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(wr.getsampwidth()),
        channels=wr.getnchannels(),
        rate=wr.getframerate(),
        output=True
    )
    chunk = 1024
    data = wr.readframes(chunk)
    while data:
        stream.write(data)
        data = wr.readframes(chunk)
    sleep(.5)
    stream.close()
    p.terminate()

def create_separeted_wavbytes(list_of_text):
    global wav_file_list
    for i, elm in enumerate(list_of_text):
        if elm:
            query = voicevox_post_audio_query(elm)
            wav_bytes = voicevox_post_synthesis(query)
            wav_file_list.append(wav_bytes)
            print(f'wav_{i} is created')
        else:
            # elmが空欄の場合は、無視。
            pass

    wav_file_list.append('====END====')
    print(f'END is appended to the list.')

def play_separated_wavbytes():
    global wav_file_list
    i = 0            

    while True:
        try:
            wav_bytes = wav_file_list.pop(0)
            if wav_bytes == '====END====':
                print('all proccess is done.')
                break
            else:
                print(f'wav_{i} now playing.')
                play_wavbytes(wav_bytes)
                i += 1
        except Exception:
            print('wait 1s')
            sleep(1)
            continue