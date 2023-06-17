# import requests
# from bs4 import BeautifulSoup

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