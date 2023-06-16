import json
import requests

google_search = {
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

def exec_google_search(query: str, num_results: int, api_key: str, cse_id: str):
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