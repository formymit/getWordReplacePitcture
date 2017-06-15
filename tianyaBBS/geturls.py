#!usr/bin/env python3.6
#-*- coding:utf-8 -*-
"""
@author:iBoy
@file: geturls.py
@time: 2017/06/08
"""
import requests
from lxml import etree
import re
import time
import random
import urllib.request
from mongodb_queue import MongoQueue
import multiprocessing
import sys

#
# keyword = '羽绒服洗涤'
# KEYWORD = urllib.request.quote(keyword)



#https://zhidao.baidu.com/search?word=%D3%F0%C8%DE%B7%FE%CF%B4%B5%D3&ie=gbk&site=-1&sites=0&date=0&pn=0
#https://zhidao.baidu.com/search?word=羽绒服洗涤&ie=gbk&site=-1&sites=0&date=0&pn=0
#需要编码 关键词  写一个通用文件 和配置文件

# url= 'https://zhidao.baidu.com/search?word=%D3%F0%C8%DE%B7%FE%CF%B4%B5%D3&ie=gbk&site=-1&sites=0&date=0&pn=0' # 0， 10 ， 20...
# url = 'https://zhidao.baidu.com/search?word=' + KEYWORD + '&ie=gbk&site=-1&sites=0&date=0&pn=0'


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:53.0) Gecko/20100101 Firefox/53.0'
}

spider_queue = MongoQueue('baiduzhidao', 'keywords')

def infoCawler():
    while True:
        try:
            keyword = spider_queue.pop()
            keyword1 = keyword[:-1] # delete \n
            print(keyword1)
        except KeyError:
            print('队列中没有数据啦~')
        else:
            getAllurls(keyword1)
            spider_queue.complete(keyword)


def geturls(url, keyword):
    try:
        total_page = 1
        response = requests.get(url, headers=headers)
        # print(response.encoding)
        response.encoding = 'utf-8'

        selector = etree.HTML(response.text)

        all_titles = selector.xpath('//h3//a')  #the same label a
        all_hrefs = selector.xpath('//h3//a/@href')  #the same label a

        total_page_str = selector.xpath('//div[@class="long-pages"]//em//text()')  #有无可能解析不到数据？？

        for i in range(len(all_titles)):
            title = all_titles[i].xpath('string(.)')
            href = all_hrefs[i]
            print(title + ', ' + href)
            with open('/Users/iBoy/PycharmProjects/SpeechOcean/day13/tianyaBBS/urls/'+ keyword+'.txt', 'a') as f:  # keyword optimization
                f.write(title + '\t' + href + '\n')

        total_page = int(total_page_str[0][2:-4]) #正则提取数字更好

    except Exception as e:
        print(str(e))
    return total_page

def getAllurls(keyword):
    try:
        KEYWORD = urllib.request.quote(keyword.encode('utf-8'))  #非常关键的编码问题！！
        url = 'http://search.tianya.cn/bbs?q=' + KEYWORD + '&pn='+ '1'
        total_page = geturls(url, keyword)

        for i in range(2, int(total_page/10) + 1):
            print('正在抓取'+ '"' + keyword+ '"'+ '的%s页'%i)
            url = 'http://search.tianya.cn/bbs?q=' + KEYWORD + '&pn=' + str(i)
            geturls(url, keyword)
            time.sleep(1.0+ random.random())
    except Exception as e:
        print(e)

def process_crawler():
    process = []
    for i in range(10):
        p = multiprocessing.Process(target=infoCawler)
        p.start()
        process.append(p)
    for p in process:
        p.join()


if __name__ == '__main__':

    process_crawler()
    # url = 'http://search.tianya.cn/bbs?q=%E7%BE%BD%E7%BB%92%E6%9C%8D%E6%B4%97%E6%B6%A4'
    # geturls(url)
   #KEYWORD 写入数据库 用多进程
    # getAllurls(KEYWORD)
    # getAllurls('西装怎么洗')

    # getAllurls('燕尾服洗涤')

