from __future__ import unicode_literals
import scrapy
import logging
from quotesbot.items import GovBidItem
import json
from selenium import webdriver
# scrapy 信号相关库
from scrapy import signals
from pydispatch import dispatcher
from scrapy.utils.project import get_project_settings
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)

#特定页面，数据不生效
class GvgkDetailSpider(scrapy.Spider):
    name = "gvgkdetailSpider"

    # 将chrome初始化放到spider中，成为spider中的元素
    def __init__(self):
        settings = get_project_settings()
        path = settings.get('CHROME_RIVER')

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=path)
        super().__init__()#调用父类方法
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.GvgkDetailSpiderCloseHandle,
                           signal=signals.spider_closed
                           )

    # 信号量处理函数：关闭chrome浏览器
    def GvgkDetailSpiderCloseHandle(self, spider):
        print(f"GvgkDetailSpider: enter ")
        self.driver.quit()

    start_urls = [
        "http://www.ccgp.gov.cn",
    ]

    # filter_num =0
    def parse(self, response):
        # 本页医院信息列表urls处理
        url_list =[
            "http://www.ccgp.gov.cn/cggg/dfgg/gkzb/202007/t20200701_14579410.htm"
        ]
        for f in url_list:
            yield scrapy.Request(url=f,
                                 callback=self.parse_detail)


    def parse_detail(self, response):
        item = GovBidItem()
        tr_num = response.xpath("count(//tr)").extract_first()
        len = int(float(tr_num))
        key_dict = {"采购项目名称": "projectName", "品目": "pingmu", "采购单位": "purUnit", "行政区域": "adminiArea",
                    "公告时间": "bulletTime",
                    "获取招标文件时间": "obtBidTime", "招标文件售价": "bidDocPrice", "获取招标文件的地点": "obtBidLoc", "开标时间": "staBidTime",
                    "开标地点": "staLoc", "预算金额": "budget", "项目联系人": "proContact", "项目联系电话": "proPhone",
                    "采购单位地址": "purAddress",
                    "采购单位联系方式": "purUnitPhone", "代理机构名称": "agentName", "代理机构地址": "agentAddress",
                    "代理机构联系方式": "agentPhone"}
        keys = list(key_dict.keys())
        for i in range(1, len + 1):
            td_num = response.xpath("count(//tr[position()=" + str(i) + "]/td)").extract_first()
            if td_num is not None:
                tr_len = int(float(td_num))
                if tr_len >= 2:
                    for j in range(1, tr_len + 1, 2):
                        tdstr = response.xpath(
                            'string(//tr[position()=' + str(i) + ']/td[' + str(j) + '])').extract_first()
                        if tdstr in keys:
                            item[key_dict.get(tdstr, "")] = response.xpath(
                                'string(//tr[position()=' + str(i) + ']/td[' + str(j + 1) + '])').extract_first()

        apd_dic = {}
        appd = response.xpath("//tr/td/*[name()='a']/text()").extract()
        hrefs = response.xpath("//tr/td/*[name()='a']/@href").extract()
        if appd is not None:
            for i, key in enumerate(appd):
                if appd[i] != "":
                    apd_dic[key] = self.base + hrefs[i]
            if apd_dic:
                item["appendix"] = json.dumps(apd_dic, ensure_ascii=False)
        return item

        # 设置随机访问时间间隔 为3-5秒 ,custom_settings覆盖settings配置
        # 在settings文件中不能单独地为某个Spider设置指定的Pipeline。需要利用Spider类属性custom_settings来实现
        # settings中设置多个pipeline可以是针对一个spider的数据，可以分别是数据清洗和持久化顺序执行

    custom_settings = {
        "RANDOM_DELAY": 5,
        "DOWNLOADER_MIDDLEWARES": {
            'quotesbot.middlewares.SeleniumMiddleware': 543,
            # "quotesbot.random_delay_middleware.RandomDelayMiddleware": 999,
            # 将scrapy默认的user-agent中间件关闭
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None

        },
        'ITEM_PIPELINES': {'quotesbot.pipelines.GovBidPipeline': 300, }
    }


