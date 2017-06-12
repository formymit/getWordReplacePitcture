#!usr/bin/env python3.6  
#-*- coding:utf-8 -*-  
""" 
@author:iBoy 
@file: getContent.py 
@time: 2017/06/10 
"""
import requests
from lxml import etree
import time
import random
from mongodb_queue import MongoQueue
import multiprocessing

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:53.0) Gecko/20100101 Firefox/53.0'
}
spider_queue = MongoQueue('baiduzhidao', 'all_urls_0612')

def getInfo():
    while True:
        try:
            url = spider_queue.pop()
            belongtoFile = spider_queue.pop_belongtoFile(url)
            print(url)
        except KeyError:
            print('队列没有数据了')
            break
        else:
            getdata(url, belongtoFile)
            spider_queue.complete(url)


def getdata(url, belongtoFile):
    try:
        response = requests.get(url, headers=headers)

        response.encoding = 'gbk'
        # print(response.text)

        selector = etree.HTML(response.text)

        #----------------------问题标题-------------------------
        all_ask_titles = selector.xpath('//h1[@accuse="qTitle"]//span[@class="ask-title "]')
        ask_title = ''
        for each in all_ask_titles:
            ask_title = each.xpath('string(.)')
            ask_title = ' '.join(ask_title.split())

        #----------------------问题正文-------------------------
        all_ask_contents = selector.xpath('//div[@accuse="qContent"]//span[@class="con-all"]')
        if len(all_ask_contents) == 1:
            ask_content = all_ask_contents[0].xpath('string(.)')
        else:
            all_ask_contents = selector.xpath('//div[@accuse="qContent"]//span[@class="con"]')
            if len(all_ask_contents) == 1:
                ask_content = all_ask_contents[0].xpath('string(.)')
            else:
                # 没有正文的情况处理
                ask_content = ''

        # ----------------------最佳答案-------------------------
        all_best_answers = selector.xpath('//pre[@class="best-text mb-10"]')
        best_answer = ''
        for each in all_best_answers:
            best_answer = each.xpath('string(.)')

        if len(best_answer) != 0:
            # 如果有最佳答案 再提取最佳答案发布时间和作者 否则 这个时间为空
            best_answer_time = selector.xpath('//span[@class="grid-r f-aid pos-time answer-time f-pening"]//text()')[0]
            best_answer_time = best_answer_time.replace('\n', '')

            best_answers_author_tmp = selector.xpath('//p[@class="mb-5"]//a//text()')
            #数组取值养成判断的习惯
            if len(best_answers_author_tmp) == 0:
                best_answers_author = '网友推荐'
            else:
                best_answers_author = best_answers_author_tmp[0]
                best_answers_author = best_answers_author.replace('\n', '')
        else:
            best_answer_time = ''
            best_answers_author = ''

        # ----------------------其他答案-------------------------
        all_other_answers = selector.xpath('//div[@class="answer-text line"]')  #con-all
        all_other_answer_time = selector.xpath('//span[@class="pos-time"]//text()')

        #其他答案放到一个数组中
        other_answer_list = []
        #如果i==0 other_answer_list 则为空
        for i in range(len(all_other_answers)):
            other_answer = all_other_answers[i].xpath('.//span[@class="con-all"]')
            #存在con-all 解析 否则解析con的即可
            if len(other_answer) == 1:
                other_answer = other_answer[0].xpath('string(.)')
            else:
                other_answer = all_other_answers[i].xpath('.//span[@class="con"]')
                if len(other_answer) != 0:
                    other_answer = other_answer[0].xpath('string(.)')
                else:
                    other_answer = ''
            other_answer  = ' '.join(other_answer.split())

            #发布时间
            other_answer_time = all_other_answer_time[i]
            other_answer_time = other_answer_time.replace('\n', '')

            #作者
            all_other_answer_author = selector.xpath('//div[@class="grid pt-5"]') #i separated...
            other_answer_author_temp = all_other_answer_author[i].xpath('.//a/text()') #别丢text()
            if len(other_answer_author_temp) == 0:
                other_answer_author = '热心网友'
            else:
                other_answer_author = other_answer_author_temp[0]
                other_answer_author = other_answer_author.replace('\n', '')

            other_answer_dict = {
                'other_anwser': other_answer,
                'other_answer_author': other_answer_author,
                'other_answer_post_time': other_answer_time

            }
            other_answer_list.append(other_answer_dict)


        data = {
            'ask_title': ask_title,
            'url': url,
            'ask_content': ask_content,
            'best_answer': best_answer,
            'best_answers_author': best_answers_author,
            'best_answer_post_time': best_answer_time,
            'other_answer_info': other_answer_list
        }
        print(data)

        #数据存入根据belongFile来存

        with open('/root/lt/day11/scrapy_Pro/baiduZhidao/data2/'+ belongtoFile, 'a') as f:
            f.write(str(data) + '\n')
    except Exception as e:
        print(e)

def process_crawler():
    process = []
    for i in range(30):
        p = multiprocessing.Process(target=getInfo)
        p.start()
        process.append(p)
    for p in process:
        p.join()


if __name__ == '__main__':

    process_crawler()
    # with open('urls.txt', 'r') as f:
    #     url = f.readline()
    #     print(url[:-1])
    #     while url:
    #         getdata(url[:-1])
    #         time.sleep(random.random())
    #         url = f.readline()
    #         print(url[:-1])


    # url = 'https://zhidao.baidu.com/question/454511374623095005.html?fr=iks&word=%B3%C4%C9%C0%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/555130249.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/1512440158180567380.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/2014834327338057748.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/1961363720699012740.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/139168816.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'http://zhidao.baidu.com/question/264474391.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/429659291231957572.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # url = 'https://zhidao.baidu.com/question/685725289752317692.html?fr=iks&word=%CC%F5%C8%DE%CF%B4%B5%D3&ie=gbk'
    # getdata(url)