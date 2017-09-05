import os
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient

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


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0

    def save(self):
        print(self.__dict__)
        mondb.movie.insert(self.__dict__)



def cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename = '{}.html'.format(url.split('=', 1)[-1])
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
        return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def get(url):
    return cached_url(url)


def download_image(url, filename):
    # 通过 url 获取到该图片的数据并写入文件
    r = requests.get(url)

    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)

    with open(path, 'wb') as f:
        f.write(r.content)


def save_cover(movies):
    for m in movies:
        filename = '{}_jpg'.format(m.ranking)
        download_image(m.cover_url, filename)


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    m = Movie()
    m.name = e('.title').text() + e('.other').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic em').text()
    m.save()

    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    page = get(url)
    e = pq(page)
    items = e('.item')
    # 调用 movie_from_div 
    movies = [movie_from_div(i) for i in items]
    return movies


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        print('top250 movies', movies)
        save_cover(movies)


if __name__ == '__main__':
    main()
