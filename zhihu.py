# -*- coding: utf-8 -*-

import os
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient
from utils import log
from config import cookie
from config import authorization

client = MongoClient()
mondb = client.mondb


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Message(Model):
    """
    存储具体信息
    """

    def __init__(self):
        self.title = ''
        self.name = ''
        self.summary = ''
        self.content_url = ''
        self.vote = 0

    def save(self):
        print(self.__dict__)
        mondb.zhihu.insert(self.__dict__)


def cached_url(url, headers):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached1'
    filename = '{}.html'.format(url.split('?', 1)[-1])
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
        return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'authorization': authorization,
        'Cookie': cookie
    }
    return cached_url(url, headers)



def message_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    m = Message()
    m.title = e('h2').text().encode('latin1').decode('utf-8')
    m.name = e('.author-link').text().encode('latin1').decode('utf-8')
    m.summary = e('.summary').text().encode('latin1').decode('utf-8')
    m.content_url = e('.toggle-expand').attr('href')
    m.vote = e('.zm-item-vote-count').text()
    m.save()
    return m


def message_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    page = get(url)
    print('page', page)
    e = pq(page)
    items = e('.feed-item')

    # 调用 movie_from_div
    for i in items:
        message_from_div(i)


def main():
    for n in range(0, 20, 5):
        print(n)
        url = 'https://www.zhihu.com/node/ExploreAnswerListV2?params=%7B%22offset%22%3A{}%2C%22type%22%3A%22day%22%7D'.format(n)
        message_from_url(url)


if __name__ == '__main__':
    main()
