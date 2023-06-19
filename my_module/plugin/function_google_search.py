import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


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
        "key": os.getenv('google_api_key'),
        "cx": os.getenv('google_cse_id')
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    items = data.get("items", [])

    for i in range(len(items)):
        del items[i]['kind']
        del items[i]['htmlTitle']
        del items[i]['displayLink']
        del items[i]['htmlSnippet']
        del items[i]['formattedUrl']
        del items[i]['htmlFormattedUrl']
        del items[i]['pagemap']

        if items[i].get('cacheId') is not None:
            del items[i]['cacheId']

    # with open("google_cse_sample.json","w") as f:
    #     json.dump(items, f)

    return json.dumps(items)