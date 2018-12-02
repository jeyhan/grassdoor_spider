#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import re
import requests

import sys
import json
import string
from bs4 import NavigableString

reload(sys)
sys.setdefaultencoding("utf-8")

url = "https://www.914ya.com"

head = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}


def get_main_class():
    def div_class_row_item(tag):
        return tag.has_attr('class') \
               and tag.name == 'div' and tag.attrs['class'][0] == 'row-item'

    html = requests.get(url, headers=head)
    html.encoding = 'utf-8'
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
    page = {}
    page['name'] = name
    if u'电影' in name:
        page['type'] = 'movie'
    elif u'图片' in name:
        page['type'] = 'picture'
    elif u'小说' in name:
        page['type'] = 'novel'
    else:
        page['type'] = 'wtf'
    sub_map = get_sub_list_of_main_class(main_class)
    page['sub_map'] = sub_map
    pages.append(page)

print json.dumps(pages).decode("unicode-escape")

debug_count = 0


def find_movie_player_url(player_page_url):
    html = requests.get(player_page_url, headers=head)
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, "html.parser")
    infos = soup.find_all('script', attrs={'language': 'JavaScript'})
    print infos[0].contents[0]

    return ''


# 从影片详情页分析影片的各项数据
def handle_movie_play_page(movie_url):
    def div_class_info(tag):
        return tag.has_attr('class') \
               and tag.name == 'div' and tag.attrs['class'][0] == 'info'

    def div_class_play_list(tag):
        return tag.has_attr('class') \
               and tag.name == 'div' and tag.attrs['class'][0] == 'play-list'

    def div_class_download_url(tag):
        return tag.has_attr('class') \
               and tag.name == 'div' and tag.attrs['class'][0] == 'downurl'

    html = requests.get(movie_url, headers=head)
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, "html.parser")
    infos = soup.find_all(div_class_info)
    video_info = {}
    for info in infos:
        for content in info.contents:
            if not isinstance(content, NavigableString):
                if isinstance(content.contents[1], NavigableString):
                    key = content.contents[0].contents[0]
                    key = str(key).replace("：", "")
                    key = key.strip()
                    if u'演员' in key:
                        video_info['actor'] = content.contents[1]
                    elif u'日期' in key:
                        video_info['date'] = content.contents[1]
                    elif u'长度' in key:
                        video_info['time_length'] = content.contents[1]
                    elif u'大小' in key:
                        video_info['video_size'] = content.contents[1]
                    elif u'画质' in key:
                        video_info['quality'] = content.contents[1]
                    elif u'分辨率' in key:
                        video_info['resolution'] = content.contents[1]
                    elif u'介绍' in key:
                        video_info['detail'] = content.contents[1]

    player_url = soup.find(div_class_play_list).contents[0].attrs['href']
    video_info['player_url'] = find_movie_player_url(url + player_url)
    downurl = soup.find(div_class_download_url).contents[0].contents[0]
    video_info['download_url'] = downurl
    return video_info


# 所有电影分类
def handle_movie(page):
    def div_class_video_pic(tag):
        return tag.has_attr('class') \
               and tag.name == 'a' and tag.attrs['class'][0] == 'video-pic'

    # 偷拍自拍，中文无码。
    for sub_item in page['sub_map']:
        movie_page_list = [sub_item['sub_href']]
        for i in range(2, 10):
            movie_page_list.append(sub_item['sub_href'] + str(i) + '.htm')
        print page['name']

        for page_url in movie_page_list:
            html = requests.get(page_url, headers=head)
            html.encoding = 'utf-8'
            soup = BeautifulSoup(html.text, "html.parser")
            videos = soup.find_all(div_class_video_pic)
            if len(videos) > 0:
                print page_url
            for video in videos:
                global debug_count
                debug_count += 1
                if debug_count > 1:
                    return
                movie_page_url = url + video.attrs['href']
                video_info = handle_movie_play_page(movie_page_url)

                print video.attrs['data-original']
                print video.attrs['title'], movie_page_url
                print json.dumps(video_info).decode("unicode-escape")


def handle_picture(page):
    print 'handle_picture'


def handle_novel(page):
    print 'handle_novel'


def handle_all_download(pages):
    for page in pages:
        if page['type'] == 'movie':
            handle_movie(page)
        elif page['type'] == 'picture':
            handle_picture(page)
        elif page['type'] == 'novel':
            handle_novel(page)


handle_all_download(pages)
