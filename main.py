# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
import requests
import collections as cl
import json


"""
Automation attach tag to pocket
"""

# IN OUT files name
IN_JSON_FILE = 'pocket_data.json'
OUT_JSON_FILE = 'add_tag_pocket_data.json'

# Set limit character count
LIMIT_CHAR_COUNT = 100


def read_json_data():
    with open(IN_JSON_FILE, 'r') as r:
        return json.load(r)


def write_result_json(data):
    with open(OUT_JSON_FILE, 'w') as w:
        json.dump(data, w)


def create_mst_tag_list(dict_data):
    mst_tag_list = []
    for i in dict_data.keys():
        if(dict_data[i]['tags'] != ''):
            tags = dict_data[i]['tags']
            mst_tag_list.append(tags.split(','))
    return list(set(sum(mst_tag_list,[])))


def add_tag_from_link(item, mst_tags):
    text = fetch_link_page_text(item['url'])
    print("--------------> fetch link page text(title, h1, h2, h3)")
    print(text)
    word_list = get_tag_word_list(text)
    item['tags'] = get_tag_words(word_list, mst_tags)
    return item


def get_tag_words(word_list, mst_tags):
    tag_words = []
    for i in word_list:
        if(i in mst_tags):
            if((i in tag_words) is False):
                tag_words.append(i)

    if(len(tag_words) != 0):
        tag_words[:-1]

    return ','.join(tag_words)


def fetch_empty_tag_list(dict_data):
    empty_list = []
    for i in dict_data.keys():
        if(dict_data[i]['tags'] == ''):
            empty_list.append(dict_data[i])
    return empty_list


def fetch_link_page_text(url):
    print("Fetch url : " + url)
    text_list = []

    r = requests.get(url, timeout=5)
    r.encoding = r.apparent_encoding
    if(r.status_code == 200):
        if('html' in r.headers['Content-Type']):
            print(r.encoding)
            if(r.encoding == 'Windows-1254'):
                r.encoding = 'utf-8'
                soup = BeautifulSoup(r.text, 'lxml')
            elif(r.encoding == 'EUC-JP'):
                soup = BeautifulSoup(r.text.encode('EUC-JP'), 'lxml')
            else:
                soup = BeautifulSoup(r.text, 'lxml')

            # delete script tag
            for script in soup.find_all('script', src=False):
                script.decompose()

            # fetch text from tag of title, h1, h2, h3
            text_list.append(soup.title.string)

            for text in soup.find_all('h1'):
                text_list.append(text.string)
            for text in soup.find_all('h2'):
                text_list.append(text.string)
            for text in soup.find_all('h3'):
                text_list.append(text.string)
            text_list2 = [t for t in text_list if t]

            res = ','.join(text_list2)
            return res.replace(' ', '')
    else:
        return ""


def get_tag_word_list(text):
    if(text is None or len(text) == 0):
        return []

    t = Tokenizer()
    tag_list = []

    # text = text.encode("raw_unicode_escape").decode("utf-8")

    for token in t.tokenize(text[0:LIMIT_CHAR_COUNT:]):
        part_of_speech = token.part_of_speech.split(',')[0]
        if part_of_speech == u'名詞':
            tag_list.append(token.surface)

    # debug
    print(tag_list)
    return tag_list


def main():
    d = read_json_data()
    mst_tags = create_mst_tag_list(d)
    target_items = fetch_empty_tag_list(d)

    # debug
    print(mst_tags)

    for item in target_items:
        res = add_tag_from_link(item, mst_tags)
        print("title : ", res['title'])
        print("Add tags --------> ", res['tags'])
        d.update(res)

    write_result_json(d)
    print("-----------------> successful")


main()
