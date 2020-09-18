from __future__ import unicode_literals
import scrapy
import logging
from quotesbot.items import GovBidXjItem
import datetime
from dateutil.relativedelta import relativedelta
import json
from selenium import webdriver
# scrapy 信号相关库
from scrapy import signals
from pydispatch import dispatcher

from scrapy.utils.project import get_project_settings
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

#询价三个月、今日数据
# " 今日0  近3日1  近1周2  近1月3  近3月4  近半年5  指定时间"
class ThrMonxjBid(scrapy.Spider):
    name = "ThreeMonXj"
    base = "http://www.ccgp.gov.cn"
    # 标题过滤列表
    filter_list = ["信息", "医疗", "系统", "软件", "绩效", "数字", "电子", "技术", "维护", "管理", "项目", "服务", "接口"]

    today = datetime.date.today()
    end_time = today.strftime('%Y:%m:%d')
    start_time = (today - relativedelta(months=+3)).strftime('%Y:%m:%d')

    baseUrl = "http://search.ccgp.gov.cn/bxsearch?"
    paraS = "searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=3&bidType="
    paraE = "&displayZone=&zoneId=&pppStatus=0&agentName="
    paraM = "&dbselect=bidx&kw=医院"
    seTime = "&start_time=" + start_time + "&end_time=" + end_time + "&timeType=4"

    # url_xj3询价三个月
    url_xj3 = baseUrl + paraS + "2" + paraM + seTime + paraE

    # 将chrome初始化放到spider中，成为spider中的元素
    def __init__(self):
        settings = get_project_settings()
        path= settings.get('CHROME_RIVER')

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=path)
        super().__init__()#调用父类方法
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.ThrMonxjBidCloseHandle,
                           signal=signals.spider_closed
                           )

    # 信号量处理函数：关闭chrome浏览器
    def ThrMonxjBidCloseHandle(self, spider):
        print(f"ThrMonxjBidCloseHandle: enter ")
        self.driver.quit()

    start_urls = [
        url_xj3,
    ]

    def parse(self, response):
        # 本页医院信息列表urls处理
        for titUrl in response.xpath("//ul[@class='vT-srch-result-list-bid']/li"):
            url = titUrl.xpath("./a/@href").extract()[0]
            title = titUrl.xpath("string(./a)").extract()[0]
            title = title.strip()
            for f in self.filter_list:
                if f in title:
                    yield scrapy.Request(url=url,
                                         callback=self.parse_detail)
                    break

        # 获取next_page_url发送氢请求
        try:
            next = response.xpath("//a[@class='next']/@onclick").extract_first()
            if next != "" and next is not None:
                nextPageNum = next[next.index("(") + 1:next.index(")")]

                if int(nextPageNum) >= 1:
                    next_url = self.url_xj3.replace("page_index=1", "page_index=" + nextPageNum)
                    yield scrapy.Request(url=next_url,
                                          callback=self.parse,
                                          dont_filter=True)  # 不去重
        except:
            print("Next page Error")
            return

    def parse_detail(self, response):
        item = GovBidXjItem()
        tr_num =  response.xpath("count(//tr)").extract_first()
        len = int(float(tr_num))

        key_dict={"采购项目名称":"projectName","品目":"pingmu","采购单位":"purUnit","行政区域":"adminiArea","公告时间":"bulletTime",
                  "获取采购文件时间":"obtBidTime","预算金额":"budget","项目联系人":"proContact","项目联系电话":"proPhone","采购单位地址":"purAddress",
                  "采购单位联系方式":"purUnitPhone","代理机构名称":"agentName","代理机构地址":"agentAddress","代理机构联系方式":"agentPhone"}
        keys = list(key_dict.keys())
        for i in range(1,len+1):
            td_num = response.xpath("count(//tr[position()="+str(i)+"]/td)").extract_first()
            if td_num is not None:
                tr_len=int(float(td_num))
                if tr_len >=2:
                    for j in range(1, tr_len+1, 2):
                        tdstr = response.xpath('string(//tr[position()='+str(i)+']/td['+str(j)+'])').extract_first()
                        if tdstr in keys:
                            item[key_dict.get(tdstr,"")] = response.xpath('string(//tr[position()='+str(i)+']/td['+str(j+1)+'])').extract_first()
        apd_dic = {}
        appd = response.xpath("//tr/td/*[name()='a']/text()").extract()
        hrefs = response.xpath("//tr/td/*[name()='a']/@href").extract()
        if appd is not None:
            for i,key in enumerate(appd):
                if appd[i] != "":
                    if "http" not in hrefs[i]:
                        apd_dic[key] = self.base + hrefs[i]
                    else:
                        apd_dic[key] = hrefs[i]
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
            # 将scrapy默认的user-agent中间件关闭
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None

        },
        'ITEM_PIPELINES': {'quotesbot.pipelines.GovBidXjPipeline': 300, }
    }


