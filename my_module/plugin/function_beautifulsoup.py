# builtin
import requests
import json

# third party
from bs4 import BeautifulSoup

web_scraper = {
                "name": "web_scraper",
                "description": "This is a tool for investigating the contents of a specific URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "This is a target url for investigating.",
                        },
                    },
                    "required": ["url"],
                },
            }

def exec_web_scraper(function_arguments):
    # arg = json.loads(function_arguments)
    # url = arg.get('url')

    response = requests.get(function_arguments)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1").text
    paragraphs = soup.find_all("p")
    description = soup.find('meta', attrs={'name': 'description'})['content']
    print(description)

    for p in paragraphs:
        print(p.text)


if __name__=='__main__':
    exec_web_scraper("https://news.yahoo.co.jp/pickup/6466856")
    # items = response.json().get("articles", [])
    # return json.dumps(items)

# # Make a request to the webpage
# url = "https://news.yahoo.co.jp/"
# response = requests.get(url)

# # Create a BeautifulSoup object
# soup = BeautifulSoup(response.text, "html.parser")

# # Find and extract specific elements from the webpage
# title = soup.find("h1").text
# paragraphs = soup.find_all("p")

# # Print the extracted data
# print("Title:", title)
# print("Paragraphs:")
# for p in paragraphs:
#     print(p.text)