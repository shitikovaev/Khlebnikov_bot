import requests
from bs4 import BeautifulSoup
import re
import json
import string
from lxml import html

url = "https://www.stihi-rus.ru/1/Hlebnikov/"


# Returns HTML Code of a page
def getHtml(url):
    response = requests.get(url)
    return response.text


# Returns a list of URLs of all Khlebnikov's poems
def getPages():
    html = getHtml(url)
    soup = BeautifulSoup(html, 'lxml')
    poems_list = soup.find('td', attrs={'valign': 'top'})  # Links are inside this tag
    poem_urls = poems_list.find_all('a')
    poem_urls = [poem_url.attrs['href'] for poem_url in poem_urls]
    return poem_urls


# retuns a list of poems
def getPoems():
    poem_urls = getPages()
    poems = []
    poem_pages = [getHtml(url + x) for x in poem_urls]
    for poem_page in poem_pages:
        soup = BeautifulSoup(poem_page, 'lxml')
        poems.append(soup.find('font', attrs={'face': 'Arial'}).text)  # Poem are inside this tag
    return poems


# cleans this list, puts into file, lemmatizes them and puts into another file.
def makeFiles():
    poems = getPoems()

    # website is old and uses old Windows \r\n format to wrap lines. we clean poems from \r
    poems = [re.sub('\r', '', x) for x in poems]
    poems = [x.strip() for x in poems]
    with open('resources/json/poems.json', 'w', encoding='utf8') as f:
        json.dump(poems, f, ensure_ascii=False)

    # list of poems without line breaks, tabs, punctuation and multiple spaces for analyzing by pymorphy
    poems_clean = []
    for poem in poems:
        poem = re.sub('\n', ' ', poem)
        poem = re.sub('\t', ' ', poem)
        poem = re.sub('\"', '', poem)

        # Clean from punctuation. Found on stackoverflow
        poem = poem.translate(str.maketrans('', '', string.punctuation))

        # Clean from spaces and spacing symbols
        poem = re.sub('\s\s+', ' ', poem)
        poem = re.sub(' +', ' ', poem)
        poems_clean.append(poem)
    with open('resources/json/poems_clean.json', 'w', encoding='utf8') as f:
        json.dump(poems_clean, f, ensure_ascii=False)

# makeFiles()
