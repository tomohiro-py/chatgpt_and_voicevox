from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import asyncio
import aiohttp
import queue
import wave
import io
import json
import string
from time import sleep

from speech_recognition import WaitTimeoutError, UnknownValueError, RequestError
import pyaudio
import openai
from vosk import SetLogLevel
SetLogLevel(-1)

import config


def setup_openai():
    openai.api_key = config.openai_api_key

def take_five():
    print("5びょうおひるねします...")
    for i in reversed(range(1,6)):

        if i == 1:
            print("{}s...".format(i), flush=True)
        else:
            print("{}s...".format(i), flush=True, end='')
        
        sleep(1)

def speech_to_text(recognizer, source, service='google'):

    while True:
        try:
            print('おはなしして！')
            voice = recognizer.listen(source, timeout=10.0, phrase_time_limit = 10.0)

            print('にんしきちゅう...')
            if service == 'google':
                text = recognizer.recognize_google(voice, language="ja-JP")
            elif service == 'vosk':
                text = json.loads(recognizer.recognize_vosk(voice, language="ja-JP"))['text'].replace(' ','')
        
            if text != '':
                break
        except WaitTimeoutError:
            print('timeout_error')
            take_five()
        except KeyboardInterrupt:
            print('Stopped')
            raise KeyboardInterrupt
        except UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception:
            # eが空っぽい。
            # print(e)
            print('An Unknown Error has occurred')
            # take_five()
    return text


async def achat(messages, response_queue):

    res = openai.ChatCompletion.acreate(
        model=config.openai_model_name,
        max_tokens=config.openai_max_tokens,
        temperature=0,
        stream=True,
        messages=messages
        )
    
    words = []
    chat_response = []

    async for chunk in await res:
        choices = chunk.choices[0]

        if 'content' in choices.delta.keys():
            content = choices.delta.content
            words.append(content)
            chat_response.append(content)
            print(content, end="", flush=True)

            # if any(char in string.punctuation for char in content):
            # promptで句読点を工夫すれば使えるかも。
            if  '。' in content or '？' in content or '！' in content:
                sentence = ''.join(words)
                await response_queue.put(sentence)
                words.clear()

        elif choices.finish_reason == 'stop':
            print('', flush=True)
            await response_queue.put('[DONE]')
        
    return ''.join(chat_response)

        
async def voicevox_text_to_query(session, response_queue, query_queue):
    while True:
        try:
            item = await asyncio.wait_for(response_queue.get(), timeout=15)
            if item == '[DONE]':
                await query_queue.put('[DONE]')
                break
        except asyncio.TimeoutError:
            break
        except Exception as e:
            break

        params = {'text': item, 'speaker': config.voicevox_charactor_id}

        async with session.post('http://127.0.0.1:50021/audio_query', params=params) as res:
            byte_str = await res.read()
            query = byte_str.decode('utf-8')

        await query_queue.put(query)
        response_queue.task_done()


async def voicevox_query_to_synthesis(session, query_queue, synthesis_queue, co_process_queue) -> bytes:
    
    while True:
        try:
            audio_query_response_json = await asyncio.wait_for(query_queue.get(), timeout=15)
            if audio_query_response_json == '[DONE]':
                co_process_queue.put('[DONE]')
                break
        except asyncio.TimeoutError:
            break
        except Exception as e:
            break
        
        params = {'speaker': config.voicevox_charactor_id}
        headers = {'content-type': 'application/json'}

        async with session.post('http://127.0.0.1:50021/synthesis', 
                                data=audio_query_response_json, 
                                headers=headers, 
                                params=params) as res:
            content = await res.content.read()

        await synthesis_queue.put(content)
        co_process_queue.put(content)
        query_queue.task_done()


def play_wavbytes(co_process_queue):

    p = pyaudio.PyAudio()
    chunk = 1024

    while True:
        try:
            wav_file = co_process_queue.get(timeout=15)

            if wav_file == '[DONE]':
                break
            else:
                wr = wave.open(io.BytesIO(wav_file))
                stream = p.open(
                    format=p.get_format_from_width(wr.getsampwidth()),
                    channels=wr.getnchannels(),
                    rate=wr.getframerate(),
                    output=True
                )
                data = wr.readframes(chunk)

                while data:
                    stream.write(data)
                    data = wr.readframes(chunk)
                else:
                    stream.close()
                    sleep(.3)

        except queue.Empty:
            break
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt was detected.")
            break
        except Exception:
            break

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


async def async_chatgpt_to_voicevox(messages):
# asyncio.to_thread() is may be good for pyaudio.try it later.
    setup_openai()
    
    loop = asyncio.get_event_loop()
    response_queue = asyncio.Queue()
    query_queue = asyncio.Queue()
    synthesis_queue = asyncio.Queue()
    co_process_queue = multiprocessing.Manager().Queue()
    
    async with aiohttp.ClientSession() as session:
        with ProcessPoolExecutor(max_workers=2) as executer:
            try:
                task0 = loop.run_in_executor(executer,play_wavbytes,co_process_queue)
            except asyncio.exceptions.CancelledError:
                print("Executer is canceled")

            try:
                async with asyncio.TaskGroup() as tg:
                        task1 = tg.create_task(achat(messages, response_queue))
                        task2 = tg.create_task(voicevox_text_to_query(session, response_queue, query_queue)) 
                        task3 = tg.create_task(voicevox_query_to_synthesis(session, query_queue, synthesis_queue, co_process_queue))
            except asyncio.exceptions.CancelledError:
                print("Taskgroup is canceled.")
        return task1.result()

if __name__ == "__main__":
    
    messages = [{'role': 'system', 'content': 'あなたは優秀なAIアシスタントです。箇条書きの場合でも、必ず句読点を挿入してください。'}, {'role': 'user', 'content': 'こんにちは！'}]
    result = asyncio.run(async_chatgpt_to_voicevox(messages),debug=False)
    print(result)
    