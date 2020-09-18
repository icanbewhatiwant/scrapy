from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import scrapy
# scrapy 信号相关库
from scrapy import signals
from pydispatch import dispatcher
import random
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from quotesbot.items import TianyanchaItem

import time
import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TYSpider(scrapy.Spider):
    name = 'tyancha'
    # allowed_domains = ['tianyancha.com/']
    logger = logging.getLogger(__name__)
    last_time = datetime.datetime.now()
    user ="13590170246"
    pwd ="zuobiao888"
    label_list = ["妇科","产科","儿科","骨科","皮肤科","眼科","美容","体检","康复","养老","口腔","肿瘤"]

    # 将chrome初始化放到spider中，成为spider中的元素
    def __init__(self):
        chrome_options = Options()
        # 设置chrome禁用图片的相关设置
        prefs = {
            'profile.default_content_setting_values': {
                # 'images': 2,  # 屏蔽图片
                # 'javascript': 2,
                'plugins': 2
            }
        }
        # 添加屏蔽chrome浏览器禁用图片的设置
        chrome_options.add_experimental_option("prefs", prefs)

        # # 修改页面加载策略：尝试后有数据缺失 而且访问过快会中途需要输入验证码
        # desired_capabilities = DesiredCapabilities.CHROME
        # desired_capabilities["pageLoadStrategy"] = "none"
        # self.driver = webdriver.Chrome(r"C:\软件\chromedriver_win32\chromedriver.exe",desired_capabilities=desired_capabilities)

        self.driver = webdriver.Chrome(r"C:\软件\chromedriver_win32\chromedriver.exe",chrome_options=chrome_options)
        # self.wait = WebDriverWait(self.driver, 20)
        super().__init__()  # 调用父类方法
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.TYSpiderCloseHandle,
                           signal=signals.spider_closed
                           )

    # 信号量处理函数：关闭chrome浏览器
    def TYSpiderCloseHandle(self, spider):
        print(f"TianYanSpiderCloseHandle: enter ")
        current_time = datetime.datetime.now()
        print("耗时： {}".format((current_time - self.last_time).seconds))
        self.driver.quit()

    start_urls = [
        'https://www.tianyancha.com/login',
    ]

    def parse(self, response):
        self.driver.find_element_by_xpath('//div[@class="title"]').click()
        delay = random.randint(1, 3)
        time.sleep(delay)

        self.driver.find_element_by_xpath('//input[@id="mobile"]').clear()
        self.driver.find_element_by_xpath('//input[@id="password"]').clear()
        self.driver.find_element_by_xpath('//input[@id="mobile"]').send_keys(self.user)  # 发送登录账号
        self.driver.find_element_by_xpath('//input[@id="password"]').send_keys(self.pwd)
        delay1 = random.randint(2, 3)
        time.sleep(delay1)  # 等待 一秒 方式被识别为机器人
        self.driver.find_element_by_xpath('//div[@class="sign-in"]/div[2]/div[4]').click()
        time.sleep(8) #这里要拖动验证码 时间要长一点
        # self.driver.find_element_by_id('home-main-search').send_keys('医院')
        # self.driver.find_element_by_id('home-main-search').send_keys(Keys.ENTER)
        # time.sleep(2)
        # 爬取数据
        yield scrapy.Request(url='https://www.tianyancha.com/search/ocQ-s1?key=医院',
                             callback=self.parse_next_page,
                             dont_filter=True)

    def parse_next_page(self, response):
        # 本页信息列表urls处理
        # 判断指定的元素中是否包含了预期的字符串，返回布尔值
        # alist = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='content']/div[@class='header']/a")))
        # if alist is not None and alist !=False:
        a_list = response.xpath("//div[@class='content']/div[@class='header']/a")
        for titUrl in a_list:
            url = titUrl.xpath("./@href").extract()[0]
            if url != "" and url is not None:
                yield scrapy.Request(url=url,
                                     callback=self.parse_detail)

        # 获取next_page_url发送请求
        try:
            # nextbutton = self.wait.until(
            #     EC.visibility_of_element_located((By.XPATH, "//a[@class='num -next']")))
            # if nextbutton is not None and nextbutton != False:
            next_url = response.xpath("//a[@class='num -next']/@href").extract_first()
            if next_url != "" and next_url is not None:
                print(next_url)
                s = next_url[next_url.index("?") - 1]
                # if int(s) <= 3:
                self.logger.info("crawling ty page:" + s)
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_next_page,
                                     dont_filter=True)  # 不去重
        except:
            print("Next page Error")
            return

    def parse_detail(self, response):
        label = []
        labelStr = ""
        item = TianyanchaItem()
        # namestr = self.wait.until(
        #     EC.visibility_of_element_located((By.XPATH, "//h1[@class='name']")))
        # if namestr is not None and namestr !=False:
        # namestrDelay = random.randint(1, 3)
        # time.sleep(namestrDelay)
        item["compName"] = response.xpath("string(//h1[@class='name'])").extract_first()
        for l in self.label_list:
            if l in item["compName"]:
                label.append(l)
        if len(label) >= 1:
                labelStr = ','.join(label)
        item["label"] = labelStr

        # content = self.wait.until(
        #     EC.visibility_of_element_located(
        #         (By.XPATH, "//table[@class='table -striped-col -border-top-none -breakall']/tbody")))
        # if content is not None and content != False:
        item["regisCapital"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[1]/td[2])").extract_first()
        item["establishDate"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[2]/td[2])").extract_first()
        item["UniSociCreCode"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[3]/td[2])").extract_first()
        item["taxpIdentity"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[4]/td[2])").extract_first()
        item["compType"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[5]/td[2])").extract_first()
        item["busiTerm"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[7]/td[2])").extract_first()
        item["staffSize"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[8]/td[2])").extract_first()
        item["regisAdress"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[10]/td[2])").extract_first()
        item["busiScope"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[11]/td[2])").extract_first()
        item["busiState"] = response.xpath(
            "string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[2]/td[4])").extract_first()
        item["industry"] = response.xpath("string(//table[@class='table -striped-col -border-top-none -breakall']/tbody/tr[5]/td[4])").extract_first()
        return item

    custom_settings = {
        # "RANDOM_DELAY": 5,
        "DOWNLOADER_MIDDLEWARES": {
            'quotesbot.middlewares.TyanSelMiddleware': 543,
            # 将scrapy默认的user-agent中间件关闭
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None

        },
        'ITEM_PIPELINES': {'quotesbot.pipelines.TianyanchaPipeline': 300, }
    }