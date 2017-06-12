#!usr/bin/env python3.6  
#-*- coding:utf-8 -*-  
""" 
@author:iBoy 
@file: wrtiteAllURLStoDB.py 
@time: 2017/06/12 
"""
import os
from mongodb_queue import  MongoQueue
spider_queue = MongoQueue('baiduzhidao', 'all_urls_0612')

#遍历文件夹 提取出文件名称和url写入数据库队列
def eachFile(filepath):
    pathDir = os.listdir(filepath) #  获取当前路径下的文件名，返回list
    for s in pathDir:
        if os.path.splitext((s))[1] == '.txt':
            print(s)
            getURLs(s)



def getURLs(filepath):

    with open('/root/lt/day11/scrapy_Pro/baiduZhidao/data/' + filepath, 'r') as f:
        url = f.readline()
        while url:
            try:
                url = url.split('\t')[1]
                print(url[:-1])
                # with open('/Users/iBoy/PycharmProjects/SpeechOcean/day12/baiduzhidao/提取url/all_urls/'+ filepath, 'a') as f2:
                #     f2.write(url)

                #写入数据库队列
                spider_queue.mypush(url[:-1], filepath)
            except Exception as e:
                print(e)
            finally:
                url = f.readline()

if __name__ == '__main__':
    filePath = '/root/lt/day11/scrapy_Pro/baiduZhidao/data/'
    eachFile(filePath)