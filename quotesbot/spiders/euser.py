# -*- coding: utf-8 -*-
import scrapy
import logging
import random

from quotesbot.items import EuserItem

logger = logging.getLogger(__name__)
class Euser(scrapy.Spider):
    name = 'euser'
    # start_urls = [
    #     'http://www.hitzone.cn/euser',
    # ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.hitzone.cn',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    detail_headers= {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'http://www.hitzone.cn/euser',
        'Host': 'www.hitzone.cn',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }


    def start_requests(self):
        self.headers['User-Agent'] = self.get_ua()
        return [scrapy.Request(url='http://www.hitzone.cn/euser',
                               headers=self.headers,
                               meta={'cookiejar': 1}, #开启cookie记录
                               callback=self.parse)]

    #parse方法默认处理start_urls的响应
    def parse(self, response):
        #选择器列表extract转换为list
        next_urls = response.xpath('//li[@class="euser_item"]/div[@class="euser_item_content"]/a[@class="logo db"]/@href').extract()
        num_urls = len(next_urls)
        logger.info("爬取urls个数："+str(num_urls)) #使用+号，逗号不会记录

        for i,url in enumerate(next_urls):
            self.detail_headers['User-Agent'] = self.get_ua()
            # if i%50 == 0:#用于随机抽取数据，发现并处理异常情况
            if url is not None:
                yield scrapy.Request(response.urljoin(url),
                                         meta={'cookiejar': response.meta['cookiejar']},#使用上一次response的cookie
                                         headers=self.detail_headers,
                                         callback=self.parse_detail)

     # 处理详情页
    def parse_detail(self, response):
        item = EuserItem()
        item['label']="医信"
        item['companyName'] = response.xpath("//div[@class='euser_hp_name tc']//text()").extract_first()

        #简介信息解析，可能有图片、不同文字解析格式
        intr_list = response.xpath("string(//li[@class='vm detail enterprise_brief'])").extract()[0]
        intr_pic = response.xpath("//li[@class='vm detail enterprise_brief']/p/descendant::img/@src").extract_first()

        if intr_list.strip()!='':
            item['introduction'] = intr_list.strip()
        elif intr_pic is not None:
            item['introduction'] = intr_pic

        #企业标签 多个返回list 逗号拼接为字符串
        comLabel = response.xpath("//div[@class='detail_wrap']/p/a[@class='db euser_cat_info']/text()").extract()
        item['comLabel'] = ','.join(comLabel)

        #解析手机和公司规模信息
        sca_tel_list = response.xpath("//div[@class='detail_wrap']/p[2]/text()").extract()#返回list中的第一个元素
        for st in sca_tel_list:
            if '公司规模' in st:
                item['scale'] = st[st.index('：') + 1:]
            if '手机' in st :
                item['telephone'] = st[st.index('：') + 1:]

        #解析注册时间和座机信息
        reg_pho_list = response.xpath("//div[@class='detail_wrap']/p[3]/text()").extract()
        for rp in reg_pho_list:
            if '注册时间' in rp:
                item['registerTime'] = rp[rp.index('：') + 1:]
            if '座机' in rp:
                item['phone'] = rp[rp.index('：') + 1:]

        #解析联系人和地址信息
        ctac_address_list = response.xpath("//div[@class='detail_wrap']/p[1]/text()").extract()
        for i in ctac_address_list:
            if '联系人' in i:
                item['contact'] =i[i.index('：') + 1:]
            if '：' not in i:
                item['address'] = i
        #解析网址信息
            item['website'] = response.xpath("//div[@class='detail_wrap']/p/a[@target]/text()").extract_first()

        # 把item传给pipeline
        # 生成器的使用
        # 好处：遍历函数的返回值的时候，挨个把数据读到内存，不会造成内存的瞬间占用过高
        # 通过yield传递数据给管道，（类似转发）
        # yield能够传递的对象只能是：BaseItem, Request, dict, None
        # 返回一条数据时，使用return 返回多条数据时，使用yield,使用一个发送给引擎一个，提高效率，少占内存
        # yield item
        return item

    def get_ua(self):
        first_num = random.randint(55, 62)
        third_num = random.randint(0, 3200)
        fourth_num = random.randint(0, 140)
        os_type = [
            '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
            '(Macintosh; Intel Mac OS X 10_12_6)'
        ]
        chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

        ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                       '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                      )
        return ua

       # 设置随机访问时间间隔 为3-5秒 ,custom_settings覆盖settings配置
    custom_settings = {
        "RANDOM_DELAY": 5,
        "DOWNLOADER_MIDDLEWARES": {
            "quotesbot.random_delay_middleware.RandomDelayMiddleware": 999,
        },
        "ITEM_PIPELINES" : {
        'quotesbot.pipelines.EuserPipeline': 300,} #300是权重，确定pipelines运行顺序，越小越优先
    }


