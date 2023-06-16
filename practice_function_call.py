import json
import requests

import openai

from my_module import config
from my_module.function_google_search import google_search, exec_google_search

def main():
    openai.api_key = config.openai_api_key
    user_message = "らかんスタジオの評判はどうですか？"
    # Step 1: ユーザーの問い合わせと利用可能な関数をモデルに送信
    response = openai.ChatCompletion.create(
        stream=True,
        model=config.openai_model_name,
        messages=[{"role": "user", "content": user_message}],
        functions=[
           google_search
        ],
        function_call="auto",
    )
    chat_response = []
    for chunk in response:
        choices = chunk.choices[0]
        # print(chunk)
        if 'content' in choices.delta.keys():
            content = choices.delta.content
            chat_response.append(content)
            print(content, end="", flush=True)

        elif choices.finish_reason == 'stop':
            print('', flush=True)

    # message = response["choices"][0]["message"]
    # # print(message)
    
    # # Step 2: モデルが関数を呼び出すかどうかを確認
    # if message.get("function_call"):
    #     function_name = message["function_call"]["name"]

    #     # Step 3: 関数を呼び出す
    #     # 注意: モデルからのJSONレスポンスは有効なJSONでない場合があります
        
    #     function_response = exec_google_search(
    #         query=json.loads(message["function_call"]["arguments"]).get("query"),
    #         num_results=json.loads(message["function_call"]["arguments"]).get("num_results"),
    #         api_key=config.google_api_key,
    #         cse_id=config.google_cse_id,
    #     )
        
        # # Step 4: モデルに関数呼び出しと関数のレスポンスについての情報を送信
        # second_response = openai.ChatCompletion.create(
        #     stream=True,
        #     model=config.openai_model_name,
        #     messages=[
        #         {"role": "user", "content": user_message},
        #         message,
        #         {
        #             "role": "function",
        #             "name": function_name,
        #             "content": function_response,
        #         },
        #     ],
        # )

        # chat_response = []
        # for chunk in second_response:
        #     choices = chunk.choices[0]

        #     if 'content' in choices.delta.keys():
        #         content = choices.delta.content
        #         chat_response.append(content)
        #         print(content, end="", flush=True)

        #     elif choices.finish_reason == 'stop':
        #         print('', flush=True)

        # return second_response

if __name__=='__main__':
    main()
