import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

"""
get api key: https://newsapi.org/
documents : https://newsapi.org/docs
request sample : https://newsapi.org/v2/everything?q=bitcoin&apiKey=943b3931ea32463d99f2feb0d4810ce7&pageSize=3
"""

newsapi_headlines = {
    "name": "newsapi_headlines",
    "description": "service of 'newsapi.com', fetch live top and breaking news headlines for a country, specific category in a country, single source, or multiple sources",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Keywords or a phrase to search for."
            },

            "category": {
                "type": "string",
                "description": "The category you want to get headlines for. \
                    Possible options: business, entertainment, general, health, science, sports, technology."
            },

             "country": {
                "type": "string",
                "description": "The 2-letter code of the country you want to get headlines for. \
                    Possible options: ae, ar, at, au, be, bg, br, ca, ch, cn, co, cu, cz, de, eg, fr, gb, gr, \
                        hk, hu, id, ie, il, in, it, jp, kr, lt, lv, ma, mx, my, ng, nl, no, nz, ph, pl, pt, ro, \
                            rs, ru, sa, se, sg, si, sk, th, tr, tw, ua, us, ve, za. \
                                Defalt: jp"
            },

            "pageSize": {
                "type": "integer",
                "description":"The number of articles included in the results. Defalt: 3"
            },

        },
    },
    "required": ["query", "country", "pageSize"],
}


def exec_newsapi_headlines(function_arguments):

    arg = json.loads(function_arguments)
    endpoint = "https://newsapi.org/v2/top-headlines"

    params = {
        "q": arg.get('query'),
        "apiKey": os.getenv('newsapi_key'),
        "pageSize": arg.get('pageSize'),
        "country": 'jp' if arg.get('country') is None else arg.get('country'),
        "category": arg.get('category')
    }
    
    response = requests.get(endpoint, params=params)
    articles = response.json().get("articles", [])

    for i in range(len(articles)):
        del articles[i]['source']
        del articles[i]['author']
        del articles[i]['urlToImage']
        del articles[i]['content']

    # with open("newsapi_headlines_sample.json","w") as f:
    #     json.dump(articles, f)

    return json.dumps(articles)

"""
RESPONSE SAMPLE

{
    "status": "ok",
    "totalResults": 11516,
    "articles": [
        {
            "source": {
                "id": "the-verge",
                "name": "The Verge"
            },
            "author": "Emma Roth",
            "title": "Mt. Gox: all the news on Bitcoin’s original biggest bankruptcy scandal",
            "description": "One of the strangest stories in crypto still isn’t over. Mt. Gox went bankrupt in 2014 after losing track of more than 650,000 Bitcoins through theft or mismanagement and its CEO was arrested. But the story didn’t end there.",
            "url": "https://www.theverge.com/2014/3/21/5533272/mt-gox-missing-bitcoins",
            "urlToImage": "https://cdn.vox-cdn.com/thumbor/cT46bayUXzTSLryuplguioQYo78=/0x0:560x372/1200x628/filters:focal(280x186:281x187)/cdn.vox-cdn.com/uploads/chorus_asset/file/10987061/mt-gox-hq.0.0.jpg",
            "publishedAt": "2023-06-09T17:28:51Z",
            "content": "Filed under:\r\nByJacob Kastrenakes, a deputy editor who oversees tech and news coverage. Since joining The Verge in 2012, hes published 5,000+ stories and is the founding editor of the creators desk. … [+17914 chars]"
        },
        {},
        {}
    ]
}
"""