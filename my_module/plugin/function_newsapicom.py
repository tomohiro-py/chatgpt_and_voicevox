import requests
import json

from . import config

"""
get api key: https://newsapi.org/
documents : https://newsapi.org/docs
request sample : https://newsapi.org/v2/everything?q=bitcoin&apiKey=943b3931ea32463d99f2feb0d4810ce7&pageSize=3
"""

newsapicom = {
    "name": "newsapicom",
    "description": "service of 'newsapi.com', \
        Search through millions of articles from over 80,000 large and small news sources and blogs. \
        This suits article discovery and analysis.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Keywords or phrases to search for in the article title and body.\
                                Advanced search is supported here:\
                                Surround phrases with quotes (\") for exact match.\
                                Prepend words or phrases that must appear with a + symbol. Eg: +bitcoin\
                                Prepend words that must not appear with a - symbol. Eg: -bitcoin\
                                Alternatively you can use the AND / OR / NOT keywords, and optionally group these with parenthesis.\
                                Eg: crypto AND (ethereum OR litecoin) NOT bitcoin.\
                                The complete value for q must be URL-encoded. Max length: 500 chars."
            },
            "pageSize": {
                "type": "integer",
                "description":"The number of articles included in the results. Defalt: 3."
            },
            "sortBy":{
                "type": "string",
                "description": "The order to sort the articles in.\
                                Possible options: relevancy, popularity, publishedAt.\
                                relevancy = articles more closely related to q come first.\
                                popularity = articles from popular sources and publishers come first.\
                                publishedAt = newest articles come first.\
                                Default: publishedAt"
            },

        },
    },
    "required": ["query","pageSize","sortBy"],
}


def exec_newsapicom(function_arguments):

    arg = json.loads(function_arguments)
    endpoint = "https://newsapi.org/v2/everything"

    params = {
        "q": arg.get('query'),
        "apiKey": config.newsapi_key,
        "pageSize":arg.get('pageSize'),
        "sortBy":arg.get('sortBy'),
    }

    response = requests.get(endpoint, params=params)
    items = response.json().get("articles", [])
    return json.dumps(items)


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