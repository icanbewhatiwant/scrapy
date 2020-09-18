# -*- coding: utf-8 -*-
import scrapy
import logging
import random

from quotesbot.items import EuserItem

logger = logging.getLogger(__name__)
class Euser(scrapy.Spider):
    name = 'tests'
    # start_urls = [
    #     'http://www.hitzone.cn/euser',
    # ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.hitzone.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    def start_requests(self):
        # self.headers['User-Agent'] = self.get_ua()
        return [scrapy.Request(url='http://www.hitzone.cn/euser',
                               headers=self.headers,
                               meta={'cookiejar': 1}, #开启cookie记录
                               callback=self.parse_detail)]

     # 处理详情页
    def parse_detail(self, response):
        item = EuserItem()
        item["companyName"]="test"
        item["introduction"]="test"
        item["label"]="test"
        item["scale"]="test"
        item["comLabel"]="test"
        item["registerTime"]="test"
        item["contact"]="test"
        item["telephone"]="test"
        item["phone"]="test"
        item["website"]="test"
        item["address"]="test"
        return item

       # 设置随机访问时间间隔 为3-5秒 ,custom_settings覆盖settings配置
    custom_settings = {
        "RANDOM_DELAY": 5,
        "DOWNLOADER_MIDDLEWARES": {
            "quotesbot.random_delay_middleware.RandomDelayMiddleware": 999,
        },
        "ITEM_PIPELINES" : {
        'quotesbot.pipelines.PGPipeline': 300,} #300是权重，确定pipelines运行顺序，越小越优先
    }


