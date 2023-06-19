# built in
import os
import json

# third party
import openai
from dotenv import load_dotenv

# 
from . import config
from .plugin.function_google_search import google_search, exec_google_search
from .plugin.function_newsapi import newsapi, exec_newsapi
from .plugin.function_newsapi_headlines import newsapi_headlines, exec_newsapi_headlines


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
            messages=messages,
            functions=[google_search, newsapi, newsapi_headlines],
            function_call="auto",
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
        function_name = []
        function_arg = []

        for chunk in res:
            choices = chunk.choices[0]

            if choices.delta.get('content') is not None:
                content = choices.delta.get('content')
                chat_response.append(content)
                print(content, end="", flush=True)
            
            if choices.delta.get('function_call') is not None:
                function_name.append(choices.delta.function_call.get('name'))
                function_arg.append(choices.delta.function_call.get('arguments'))

            if choices.finish_reason == 'stop':
                print('', flush=True)
                return ''.join(list(filter(None, chat_response)))
            
            elif choices.finish_reason == 'function_call':
                print(f"=== {function_name[0]} ===")
                new_messages_with_function_response = self.execute_function(
                    function_name[0],
                    json.dumps(''.join(function_arg)), 
                    messages)
                
                return self.chat_stream(new_messages_with_function_response)


    def execute_function(self, function_name:str, function_arg:str, messages:list):
        res = eval(f'exec_{function_name}({function_arg})')
        function_message = dict(role = 'function',
                                name = function_name,
                                content = res)
        new_messages_with_function_response = []
        new_messages_with_function_response.extend(messages)
        new_messages_with_function_response.append(function_message)

        return new_messages_with_function_response
        

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