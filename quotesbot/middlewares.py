# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import random
#selenium中间件
from scrapy.http import HtmlResponse
class SeleniumMiddleware(object):
    # 只有小部分页面会用到chrome，把chrome放到spider里。
    # 这样的好处：每个spider都有自己的chrome，这样当启动多个spider时，就会有多个chrome，
    # 不是所有的spider共用一个chrome，这对我们的并发是有好处的。 初始化方法放到spider中
    # def __init__(self):
    #     self.driver = webdriver.Chrome(r"C:\软件\chromedriver_win32\chromedriver.exe")

    def process_request(self, request, spider):
        try:
            if spider.name == 'seleniumSpider' or spider.name == 'govBidxj':
                spider.driver.get(request.url)
                delay = random.randint(2, 5)
                time.sleep(delay)

        except Exception as e:
            print(f"chrome getting page error, Exception = {e}")
            return HtmlResponse(url=request.url, status=500, request=request)
        else:
            time.sleep(2)
            body = spider.driver.page_source
            return HtmlResponse(spider.driver.current_url,
                                body=body,
                                encoding='utf-8',
                                request=request)

class TyanSelMiddleware(object):
    def process_request(self, request, spider):
        # print(f"chrome tianyancha is getting page")
        try:
            # if spider.name == 'tianyancha' or spider.name =="tyancha":
            if spider.name =="tyancha":
                spider.driver.get(request.url)
                # delay = random.randint(2, 3)
                # time.sleep(delay)

        except Exception as e:
            print(f"chrome tianyancha getting page error, Exception = {e}")
            return HtmlResponse(url=request.url, status=500, request=request)
        else:
            time.sleep(2)
            body = spider.driver.page_source
            return HtmlResponse(spider.driver.current_url,
                                body=body,
                                encoding='utf-8',
                                request=request)
