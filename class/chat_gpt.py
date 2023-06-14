import openai
import config

class Chatgpt:
    openai.api_key = config.openai_api_key
    model = config.openai_model_name
    max_tokens = config.openai_max_tokens
    temperature = config.openai_temperature
    total_tokens = 0

    def completion(self, messages:list, message_only:bool=True) -> str:
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

def main():
    messages = [{'role': 'user', 'content': 'はじめまして。なにかジョークをお願いします。'}]

    ai = Chatgpt()
    res = ai.completion(messages)
    print(res)
    print(ai.total_tokens)

if __name__=='__main__':
    main()