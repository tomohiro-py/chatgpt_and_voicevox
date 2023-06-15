import requests
import json
import asyncio
import aiohttp

from . import sound

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

        sound.play_wave(res.content)

    async def atext_to_query(self, response_queue, query_queue):
        while True:
            try:
                item = await asyncio.wait_for(response_queue.get(), timeout=15)
                if item == '[DONE]':
                    await query_queue.put('[DONE]')
                    break
            except asyncio.TimeoutError:
                break
            except Exception:
                break

            async with aiohttp.ClientSession() as session:
                params = {'text': item, 'speaker': self.charactor_id}
                async with session.post('http://127.0.0.1:50021/audio_query',params=params) as res:
                    byte_str = await res.read()
                    query = byte_str.decode('utf-8')

            await query_queue.put(query)
            response_queue.task_done()


    async def aquery_to_synthesis(self, query_queue, synthesis_queue, co_process_queue) -> bytes:
        while True:
            try:
                audio_query_response_json = await asyncio.wait_for(query_queue.get(), timeout=15)
                if audio_query_response_json == '[DONE]':
                    co_process_queue.put('[DONE]')
                    break
            except asyncio.TimeoutError:
                break
            except Exception:
                break

            async with aiohttp.ClientSession() as session:
                params = {'speaker': self.charactor_id}
                headers = {'content-type': 'application/json'}
                async with session.post('http://127.0.0.1:50021/synthesis', 
                                        data=audio_query_response_json, 
                                        headers=headers, 
                                        params=params) as res:
                    
                    content = await res.content.read()

            await synthesis_queue.put(content)
            co_process_queue.put(content)
            query_queue.task_done()


def main():
    vv = Voicevox()
    vv.speak(text='こんにちは')


if __name__ == "__main__":
    main()

