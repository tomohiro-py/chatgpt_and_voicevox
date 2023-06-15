from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import asyncio
from time import sleep

import speech_recognition as sr

from my_module.chat_gpt import Chatgpt
from my_module.voicevox import Voicevox
from my_module.messages import Messages
from my_module import sound


def take_five():
    print("5びょうおひるねします...")
    for i in reversed(range(1,6)):
        if i == 1:
            print("{}s...".format(i), flush=True)
        else:
            print("{}s...".format(i), flush=True, end='')
        sleep(1)


async def async_chatgpt_to_voicevox(messages):
    vv = Voicevox()
    ai = Chatgpt()
    loop = asyncio.get_event_loop()
    response_queue = asyncio.Queue()
    query_queue = asyncio.Queue()
    synthesis_queue = asyncio.Queue()
    co_process_queue = multiprocessing.Manager().Queue()

    with ProcessPoolExecutor(max_workers=2) as executer:
        try:
            task0 = loop.run_in_executor(executer,sound.play_wav_with_queue,co_process_queue)
            async with asyncio.TaskGroup() as tg:
                    task1 = tg.create_task(ai.achat(messages, response_queue))
                    task2 = tg.create_task(vv.atext_to_query(response_queue, query_queue)) 
                    task3 = tg.create_task(vv.aquery_to_synthesis(query_queue, synthesis_queue, co_process_queue))
        except asyncio.exceptions.CancelledError:
            print("asyncio.exceptions.CancelledError")
    return task1.result()


def main_loop():
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.pause_threshold = 1.5
        r.energy_threshold = 4000

        msg = Messages()
        while True:
            while True:
                try:
                    print('おはなしして！')
                    voice = r.listen(source, timeout=10.0, phrase_time_limit = 10.0)
                    print('にんしきちゅう...')
                    user_message = r.recognize_google(voice, language="ja-JP")

                    if user_message != '':
                        print(f'YOU : {user_message}')
                        break

                except sr.WaitTimeoutError:
                    print('timeout_error')
                    take_five()
                except (sr.UnknownValueError, sr.RequestError):
                    print("Google Speech Recognition could not understand audio")
                except KeyboardInterrupt:
                    print('Stopped')
                    raise KeyboardInterrupt
                except Exception:
                    print('An Unknown Error has occurred')
                    raise Exception

            if user_message == "おしまい":
                sound.play_wav('wave_file/ending.wav')
                break
            else:
                msg.add_user_message(user_message)

            messages = msg.build()
            assistant_message = asyncio.run(async_chatgpt_to_voicevox(messages))
            msg.add_assistant_message(assistant_message)

if __name__ == '__main__':
    main_loop()


        # print('ちょうせいちゅう...')
        # r.dynamic_energy_threshold = True
        # r.adjust_for_ambient_noise(source, duration=1)

        # text = json.loads(r.recognize_vosk(voice, language="ja-JP"))['text'].replace(' ','')