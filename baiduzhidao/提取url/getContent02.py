#!usr/bin/env python3.6  
#-*- coding:utf-8 -*-  
""" 
@author:iBoy 
@file: getContent.py 
@time: 2017/06/10 
"""
import os
import re
import urllib

import requests
from lxml import etree
import time
import random
from mongodb_queue import MongoQueue
import multiprocessing
import json

#获取文件当前目录
currentPath =os.path.dirname(os.path.realpath(__file__))

headers = {
    "Host": "eclick.baidu.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel… Gecko/20100101 Firefox/54.0",
    "Referer": 	"https://zhidao.baidu.com/ques…d=PU%D4%F5%C3%B4%CF%B4&ie=gb",
    "Cookie": "BAIDUID=3E29B92E01B4ACF0460CF…88E999055A3F8A630C64834BD6D0"
}

spider_queue = MongoQueue('baiduzhidao', 'all_urls_0612')


def getInfo():
    while True:
        try:
            url = spider_queue.pop()
            time.sleep(5+random.random())
            belongtoFile = spider_queue.pop_belongtoFile(url)
            # print(url)
        except KeyError:
            print('队列没有数据了')
            break
        else:
            flag = getdata(url, belongtoFile)
            if flag:
                spider_queue.complete(url)
            else:
                spider_queue.reset(url)

def getdata(url, belongtoFile):
    try:
        flag = True
        #为了更高校可以先判断一下是否需要执行下面的替换函数？
        response = requests.get(url, headers=headers)#, proxies = proxy)
        response.encoding = 'GB18030'
        out = response.text
        ########################开始字符预处理 将所有存在<img class='word replace' ...> 的标签处理掉 然后正常解析#######
        replacedWordDict = {
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0061695f310000">': '爱',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0062615f310000">': '把',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006265695f310000">': '被',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0062750000">': '不',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006368616e675f310000">': '长',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006368616e675f320000">': '常',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006368656e675f310000">': '成',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006368755f310000">': '出',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0063695f310000">': '次',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0063695f320000">': '此',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00636f6d6d610000">': ',',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00636f6e675f310000">': '从',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064615f310000">': '大',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064616e0000">': '但',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064616e675f310000">': '当',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064616f0000">': '到',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064650000">': '的',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064655f310000">': '得',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064695f310000">': '地',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00646f6e675f310000">': '动',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006475695f310000">': '对',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0064756f5f310000">': '多',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0065725f310000">': '而',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0065725f320000">': '儿',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0066615f320000">': '法',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0066616e675f310000">': '方',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0066656e5f310000">': '分',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0067616e5f310000">': '感',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0067650000">': '个',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0067756f0000">': '果',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0067756f5f310000">': '国',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0067756f5f320000">': '过',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006861695f310000">': '还',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0068616f5f310000">': '好',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0068655f310000">': '和',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0068656e0000">': '很',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00686f750000">': '后',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006875610000">': '话',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006875695f310000">': '会',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006875695f320000">': '回',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0068756f5f310000">': '活',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006a69616e670000">': '将',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006a69750000">': '就',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006b61695f310000">': '开',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006b650000">': '可',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006c61695f310000">': '来',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006c616f5f310000">': '老',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006c655f310000">': '了',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006c695f310000">': '里',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006d610000">': '吗',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006d650000">': '么',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006d656e5f310000">': '们',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006e610000">': '那',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006e690000">': '你',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006e69616e5f310000">': '年',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a006e765f310000">': '女',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0071755f310000">': '去',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007175657374696f6e0000">': '？',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0071756f74655f6c6566740000">': '"',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0071756f74655f72696768740000">': '"',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0072616e0000">': '然',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0072656e5f310000">': '人',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0072695f310000">': '日',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0072750000">': '如',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007368616e675f310000">': '上',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007368656e0000">': '什',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007368656e675f310000">': '生',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007368690000">': '是',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007368695f310000">': '时',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00736967680000">': '！',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0073746f700000">': '。',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0074615f66656d616c650000">': '她',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0074615f69740000">': '它',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0074615f6d616c650000">': '他',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007469616e5f310000">': '天',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00746f755f310000">': '头',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007765690000">': '为',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0077755f310000">': '无',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007869615f310000">': '下',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007869616f5f310000">': '小',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0078696e5f310000">': '心',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007875655f310000">': '学',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0079616e675f310000">': '样',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0079655f310000">': '也',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007969310000">': '一',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007969330000">': '以',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0079695f310000">': '己',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a0079696e5f310000">': '因',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00796f755f310000">': '有',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a00796f755f320000">': '又',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a61690000">': '在',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a656e0000">': '怎',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a68650000">': '这',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a68656e675f310000">': '正',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a68695f310000">': '只',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a68695f330000">': '之',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a686f6e670000">': '中',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a695f310000">': '子',
            '<img class="word-replace" src="https://zhidao\\.baidu\\.com/api/getdecpic\\?picenc=0a007a75690000">': '最'}
        for key in replacedWordDict.keys():
            pattern = r'%s' % key  # 非贪婪匹配  用完整的 直接替换即可 重新获取文字图片信息  src
            out = re.sub(pattern, replacedWordDict[key], out)
        # print('图片转字符处理完毕！')

        ########################处理完图片字符结束 可以正常解析啦#####################################################

        selector = etree.HTML(out)  #content better

        #----------------------问题标题-------------------------
        all_ask_titles = selector.xpath('//h1[@accuse="qTitle"]//span[@class="ask-title "]')
        ask_title = ''
        for each in all_ask_titles:
            ask_title = each.xpath('string(.)')
            ask_title = ' '.join(ask_title.split())

        #乱码问题处理
        if len(ask_title) == 0:
            #需要重新抓取 后部分解析代码不执行
            print('出现乱码...')
            flag = False

        if flag:
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

            ask_content = ' '.join(ask_content.split())
            ask_content = ask_content.replace('\n', '')
            # ----------------------最佳答案-------------------------
            all_best_answers = selector.xpath('//pre[@class="best-text mb-10"]')
            best_answer = ''
            for each in all_best_answers:
                best_answer = each.xpath('string(.)')
                #多空格处理
                best_answer = ' '.join(best_answer.split())

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

            # ----------------------其他答案  这部分代码有问题 可能乱序------------------------- 重构一下代码
            all_other_answers = selector.xpath('//div[@class="answer-text line"]')  #con-all  answer-text mb10
            all_other_answer_time = selector.xpath('//span[@class="pos-time"]//text()')

            #其他答案放到一个数组中
            other_answer_list = []
            #如果len(all_other_answers==0 other_answer_list 则为空
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
            #################第二种情况 answer-text mb-10  解析完添加到other_answer_list 即可#######

            data = {
                'ask_title': ask_title,
                'url': url,
                'ask_content': ask_content,
                'best_answer': best_answer,
                'best_answers_author': best_answers_author,
                'best_answer_post_time': best_answer_time,
                'other_answer_info': other_answer_list,

            }
            # 中文编码问题解决
            print(url)
            data = json.dumps(data ,ensure_ascii=False, sort_keys=False)
            print(data)

            #数据存入根据belongFile来存

            with open(currentPath + '/data/'+ belongtoFile, 'a') as f:
                f.write(str(data) + '\n')

    except Exception as e:
        print(e)
    return flag



def process_crawler():
    process = []
    for i in range(10):
        p = multiprocessing.Process(target=getInfo)
        p.start()
        process.append(p)
    for p in process:
        p.join()


if __name__ == '__main__':

    process_crawler()


