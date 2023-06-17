import json
import requests

from . import config

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
                    },
                    "required": ["query", "num_results",],
                },
            }

def exec_google_search(function_arg):
    # Google検索APIのエンドポイント
    endpoint = "https://www.googleapis.com/customsearch/v1"
    query = json.loads(function_arg).get("query"),
    num_results = json.loads(function_arg).get("num_results"),
    
    params = {
        "q": query,
        "num": num_results,
        "key": config.google_api_key,
        "cx": config.google_cse_id
    }

    response = requests.get(endpoint, params=params)
    data = response.json()
    items = data.get("items", [])
    return json.dumps(items)