import asyncio
import pyaudio
import wave
import io
import config
from time import sleep
import aiohttp
import openai
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import queue
import logging
import random

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s', level=logging.DEBUG)

def setup_openai():
    openai.api_key = config.openai_api_key
    logging.debug('Api key has been set up.')


async def achat(messages, response_queue):

    res = openai.ChatCompletion.acreate(
        model=config.openai_model_name,
        max_tokens=config.openai_max_tokens,
        temperature=0,
        stream=True,
        messages=messages
        )
    
    logging.debug('Chat stream start.')
    words = []
    chat_response = []

    async for chunk in await res:
        choices = chunk.choices[0]

        if 'content' in choices.delta.keys():
            content = choices.delta.content
            words.append(content)
            chat_response.append(content)
            print(content, end="", flush=True)

            if  '。' in content or '？' in content or '！' in content:
                sentence = ''.join(words)
                await response_queue.put(sentence)
                words.clear()

        elif choices.finish_reason == 'stop':
            logging.debug('Chat stream End')
            print('', flush=True)
            await response_queue.put('[DONE]')
        
    return ''.join(chat_response)

        
async def voicevox_text_to_query(response_queue, query_queue):
    while True:
        try:
            item = await asyncio.wait_for(response_queue.get(), timeout=15)
            if item == '[DONE]':
                await query_queue.put('[DONE]')
                break
        except asyncio.TimeoutError:
            logging.debug('Timeout Error')
            break
        except Exception as e:
            logging.critical(e)
            break

        logging.debug("Query Start")
        params = {'text': item, 'speaker': config.voicevox_charactor_id}

        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:50021/audio_query', params=params) as res:
                byte_str = await res.read()
                query = byte_str.decode('utf-8')

        await query_queue.put(query)
        response_queue.task_done()
        logging.debbug("Query End")


async def voicevox_query_to_synthesis(query_queue, synthesis_queue, co_process_queue) -> bytes:
    
    while True:
        try:
            audio_query_response_json = await asyncio.wait_for(query_queue.get(), timeout=15)
            if audio_query_response_json == '[DONE]':
                co_process_queue.put('[DONE]')
                break
        except asyncio.TimeoutError:
            logging.debug("Timeout error")
            break
        except Exception as e:
            logging.critical(e)
            break
        
        logging.debug("Synthesis Start")
        params = {'speaker': config.voicevox_charactor_id}
        headers = {'content-type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://127.0.0.1:50021/synthesis', 
                data=audio_query_response_json, 
                headers=headers, 
                params=params) as res:
                content = await res.content.read()

        await synthesis_queue.put(content)
        co_process_queue.put(content)
        query_queue.task_done()
        logging.debug("Synthesis End")


def play_wavbytes(co_process_queue):

    p = pyaudio.PyAudio()
    chunk = 1024

    while True:
        try:
            wav_file = co_process_queue.get(timeout=15)
            if wav_file == '[DONE]':
                logging.debug('All synthesises have been played')
                break
        except queue.Empty:
            logging.debug('co_process_queue is empty')
            break
        except Exception as e:
            logging.debug(e)
            break

        logging.debug("Player Start")
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
            logging.debug("Player End")

    p.terminate()


async def async_chatgpt_to_voicevox(messages):
# asyncio.to_thread() is may be good for pyaudio.try it later.
    setup_openai()
    
    loop = asyncio.get_event_loop()
    response_queue = asyncio.Queue()
    query_queue = asyncio.Queue()
    synthesis_queue = asyncio.Queue()
    co_process_queue = multiprocessing.Manager().Queue()

    with ProcessPoolExecutor(max_workers=2) as executer:
        task0 = loop.run_in_executor(executer,play_wavbytes,co_process_queue)

        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(achat(messages, response_queue))
            task2 = tg.create_task(voicevox_text_to_query(response_queue, query_queue)) 
            task3 = tg.create_task(voicevox_query_to_synthesis(query_queue, synthesis_queue, co_process_queue))
    
    return task1.result()

if __name__ == "__main__":
    
    messages = [{'role': 'system', 'content': 'あなたは優秀なAIアシスタントです。箇条書きの場合でも、必ず句読点を挿入してください。'}, {'role': 'user', 'content': 'こんにちは！'}]
    result = asyncio.run(async_chatgpt_to_voicevox(messages),debug=False)
    print(result)
    