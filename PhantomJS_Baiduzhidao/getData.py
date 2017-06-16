#!usr/bin/env python3.6  
#-*- coding:utf-8 -*-  
""" 
@author:iBoy 
@file: getData.py
@time: 2017/06/16 
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from lxml import etree
import parseHTML


browser = webdriver.PhantomJS()
wait =WebDriverWait (browser, 10)
browser.set_window_size(1400, 900)

def work(url):
    print('I am working....')
    try:
        browser.get(url)  #打开新的标签即可？
        html = browser.page_source

        #解析html
        parseHTML.parse(url, html, 'a.txt')

    except Exception as e:
        print(e)
        traceback.print_exc()

#html解析函数

if __name__ == '__main__':
    with open('POLO衫怎么洗.txt') as f:
        url = f.readline()
        while url:
            try:
                print(url)
                work(url[:-11])
            except Exception as e:
                print(e)
                traceback.print_exc()
            # finally:
            #     browser.quit()

            url = f.readline()



