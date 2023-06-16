import json
import requests

import openai


def google_search(query: str, num_results: int, api_key: str, cse_id: str):
    # Google検索APIのエンドポイント
    url = "https://www.googleapis.com/customsearch/v1"
    
    # リクエストパラメータ
    params = {
        "q": query,
        "num": num_results,
        "key": api_key,
        "cx": cse_id
    }
    
    # APIリクエストを送信
    response = requests.get(url, params=params)
    
    # レスポンスを解析
    data = response.json()
    items = data.get("items", [])
    
    # 検索結果をJSON形式で返す
    return json.dumps(items)

def run_conversation():
    # Step 1: ユーザーの問い合わせと利用可能な関数をモデルに送信
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[{"role": "user", "content": "Today's news in Japan?"}],
        functions=[
            {
                "name": "google_search",
                "description": "Google search, fetch real-time data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "The number of search results to return",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Your Google API key",
                        },
                        "cse_id": {
                            "type": "string",
                            "description": "Your Google Custom Search Engine ID",
                        },
                    },
                    "required": ["query", "num_results", "api_key", "cse_id"],
                },
            }
        ],
        function_call="auto",
    )

    message = response["choices"][0]["message"]
    

    # Step 2: モデルが関数を呼び出すかどうかを確認
    if message.get("function_call"):
        function_name = message["function_call"]["name"]

        # Step 3: 関数を呼び出す
        # 注意: モデルからのJSONレスポンスは有効なJSONでない場合があります
        
        function_response = google_search(
            query=json.loads(message["function_call"]["arguments"]).get("query"),
            num_results=json.loads(message["function_call"]["arguments"]).get("num_results"),
            api_key="YOUR_GOOGLE_API_KEY",
            cse_id="YOUR_GOOGLE_CES_ID",
        )
        
        # Step 4: モデルに関数呼び出しと関数のレスポンスについての情報を送信
        second_response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": "Today's news in Japan?"},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )

        return second_response

print(run_conversation())
