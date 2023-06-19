# built in
import os

# third party
import openai
from dotenv import load_dotenv

# 
from . import config

load_dotenv()


class Chatgpt:

    def __init__(self) -> None:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = config.openai_model_name
        self.max_tokens = config.openai_max_tokens
        self.temperature = config.openai_temperature
        self.total_tokens = 0
        
        
    def chat(self, messages:list, message_only:bool=True) -> str:
        res = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=False,
            messages=messages
        )

        self.total_tokens += res['usage']['total_tokens']

        if message_only:
            return res.choices[0].message.content
        else:
            return res

    
    def chat_stream(self, messages:list) -> str:
        res = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
            messages=messages
        )

        chat_response = []
        for chunk in res:
            choices = chunk.choices[0]

            if 'content' in choices.delta.keys():
                content = choices.delta.content
                chat_response.append(content)
                print(content, end="", flush=True)

            elif choices.finish_reason == 'stop':
                print('', flush=True)
            
        return ''.join(chat_response)
        

    async def achat(self, messages:list, response_queue) -> str:

        res = openai.ChatCompletion.acreate(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
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

                if  '。' in content or '？' in content or '！' in content:
                    sentence = ''.join(words)
                    await response_queue.put(sentence)
                    words.clear()

            elif choices.finish_reason == 'stop':
                print('', flush=True)
                await response_queue.put('[DONE]')
            
        return ''.join(chat_response)


def main():
    messages = [{'role': 'user', 'content': 'はじめまして。なにかジョークをお願いします。'}]

    ai = Chatgpt()
    res = ai.chat(messages, message_only=True)
    print(res)
    print(ai.total_tokens)

if __name__=='__main__':
    main()