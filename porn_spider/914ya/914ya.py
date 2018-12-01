#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import re
import requests

import sys
import json
import string

reload(sys)
sys.setdefaultencoding("utf-8")

url = "https://www.914ya.com"

head = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}


html = requests.get(url, headers=head)
html.encoding = 'utf-8'



def get_main_class():
    def div_class_row_item(tag):
        return tag.has_attr('class') \
               and tag.name == 'div' and tag.attrs['class'][0] == 'row-item'

    soup = BeautifulSoup(html.text, "html.parser")
    main_class = soup.find_all(div_class_row_item)
    return main_class


def get_name_of_main_class(main_class):
    main_class_name = main_class.find('a', attrs={'class': 'c_white'})
    return main_class_name.contents[0]


def get_sub_list_of_main_class(main_class):
    main_class_sub = main_class.find_all('a')
    main_class_sub_map = []
    for main_class_sub_item in main_class_sub:
        if main_class_sub_item.attrs['href'] != '#':
            main_sub_item = {}
            main_sub_item['sub_name'] = main_class_sub_item.contents[0]
            main_sub_item['sub_href'] = url + main_class_sub_item.attrs['href']
            main_class_sub_map.append(main_sub_item)
    return main_class_sub_map


main_classes = get_main_class()

print len(main_classes)
pages = []
for main_class in main_classes:
    name = get_name_of_main_class(main_class)
    page_info = {}
    page_info['name'] = name
    if u'电影' in name:
        page_info['type'] = 'movie'
    elif u'图片' in name:
        page_info['type'] = 'picture'
    elif u'小说' in name:
        page_info['type'] = 'novel'
    else:
        page_info['type'] = 'wtf'
    sub_map = get_sub_list_of_main_class(main_class)
    page_info['sub_map'] = sub_map
    pages.append(page_info)

print json.dumps(pages).decode("unicode-escape")