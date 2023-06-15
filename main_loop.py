from itertools import zip_longest
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import asyncio
import aiohttp
from time import sleep
import json

import speech_recognition as sr
# from speech_recognition import WaitTimeoutError, UnknownValueError, RequestError

from my_module.sound import play_wav_with_queue
from my_module.chat_gpt import Chatgpt
from my_module.voicevox import Voicevox
from my_module import sound
from my_module import config


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
        except sr.WaitTimeoutError:
            print('timeout_error')
            take_five()
        except KeyboardInterrupt:
            print('Stopped')
            raise KeyboardInterrupt
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception:
            # eが空っぽい。
            # print(e)
            print('An Unknown Error has occurred')
            # take_five()
    return text

async def async_chatgpt_to_voicevox(messages):
    
    loop = asyncio.get_event_loop()
    response_queue = asyncio.Queue()
    query_queue = asyncio.Queue()
    synthesis_queue = asyncio.Queue()
    co_process_queue = multiprocessing.Manager().Queue()

    vv = Voicevox()
    ai = Chatgpt()
    
    async with aiohttp.ClientSession() as session:
        with ProcessPoolExecutor(max_workers=2) as executer:
            try:
                task0 = loop.run_in_executor(executer,play_wav_with_queue,co_process_queue)
            except asyncio.exceptions.CancelledError:
                print("Executer is canceled")

            try:
                async with asyncio.TaskGroup() as tg:
                        task1 = tg.create_task(ai.achat(messages, response_queue))
                        task2 = tg.create_task(vv.atext_to_query(session, response_queue, query_queue)) 
                        task3 = tg.create_task(vv.aquery_to_synthesis(session, query_queue, synthesis_queue, co_process_queue))
            except asyncio.exceptions.CancelledError:
                print("Taskgroup is canceled.")
        return task1.result()


def main_loop():
    with open('my_module/system.prompt', 'r', encoding='utf-8') as f:
        system_content = f.read()

    system_message = dict(role='system', content=system_content)
    user_messages = []
    ai_messages = []
    
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.pause_threshold = 1.5
        r.energy_threshold = 4000
        # print('ちょうせいちゅう...')
        # r.dynamic_energy_threshold = True
        # r.adjust_for_ambient_noise(source, duration=1)

        while True:
            # user_content = input('YOU : ')
            user_content = speech_to_text(r,source)
            print(f'YOU : {user_content}')

            if user_content.lower() == "bye now":
                sound.play_wav('wave_file/ending.wav')
                break
            elif user_content == "おしまい":
                sound.play_wav('wave_file/ending.wav')
                break
            else:
                user_dict = dict(role='user',content=user_content)
                user_messages.append(user_dict)

            messages = []
            messages.append(system_message)

            if len(ai_messages) == 0:
                messages.extend(user_messages)
            else:
                for (user_message, ai_message) in zip_longest(user_messages, ai_messages):
                    messages.append(user_message)
                    if ai_message is not None:
                        messages.append(ai_message)
            
            ai_content = asyncio.run(async_chatgpt_to_voicevox(messages))
            ai_dict = dict(role='assistant',content=ai_content)
            ai_messages.append(ai_dict)

            if config.openai_prompt_threshold < len(user_messages):
                del user_messages[0]
                del ai_messages[0]


if __name__ == '__main__':
    main_loop()
