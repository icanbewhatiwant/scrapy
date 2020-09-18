# -*- coding: utf-8 -*-
import scrapy
from quotesbot.items import EuserItem
from scrapy.exceptions import IgnoreRequest

class ToScrapeCSSSpider(scrapy.Spider):
    # name：spider标识符，一个项目中不同spider的name不一样，是唯一的
    #start_urls 返回可迭代的URL request list，spider爬取地址，后续URL从初始的URL获取到的数据中提取。
    #parse() 每个初始URL完成下载后生成的 Response 对象将作为唯一参数传递给该函数
    #它负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。
    name = "test"
    start_urls = [
        'http://www.hitzone.cn/euser/23869.html',
        'http://www.hitzone.cn/euser/23295.html',
        'http://www.hitzone.cn/euser/28165.html'
    ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'http://www.hitzone.cn/euser',
        'Host': 'www.hitzone.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,#多个请求用yield
                                   headers=self.headers,
                                   callback=self.parse)

#带yield的函数是真正的迭代器  调用next方法，parse函数正式开始执行  把yield看作return，每次调用next从程序停止的地方开始执行
    def parse(self, response):
        item = EuserItem()
        item['label'] = "医信"
        item['companyName'] = response.xpath("//div[@class='euser_hp_name tc']//text()").extract_first()

        # 简介信息解析，可能有图片、不同文字解析格式
        intr_list = response.xpath("string(//li[@class='vm detail enterprise_brief'])").extract()[0]
        intr_pic = response.xpath("//li[@class='vm detail enterprise_brief']/p/descendant::img/@src").extract_first()

        if intr_list.strip() != '':
            item['introduction'] = intr_list.strip()
        elif intr_pic is not None:
            item['introduction'] = intr_pic

        # 企业标签 多个返回list 逗号拼接为字符串
        comLabel = response.xpath("//div[@class='detail_wrap']/p/a[@class='db euser_cat_info']/text()").extract()
        item['comLabel'] = ','.join(comLabel)

        # 解析手机和公司规模信息
        sca_tel_list = response.xpath("//div[@class='detail_wrap']/p[2]/text()").extract()  # 返回list中的第一个元素
        for st in sca_tel_list:
            if '公司规模' in st:
                item['scale'] = st[st.index('：') + 1:]
            if '手机' in st:
                item['telephone'] = st[st.index('：') + 1:]

        # 解析注册时间和座机信息
        reg_pho_list = response.xpath("//div[@class='detail_wrap']/p[3]/text()").extract()
        for rp in reg_pho_list:
            if '注册时间' in rp:
                item['registerTime'] = rp[rp.index('：') + 1:]
            if '座机' in rp:
                item['phone'] = rp[rp.index('：') + 1:]

        # 解析联系人和地址信息
        ctac_address_list = response.xpath("//div[@class='detail_wrap']/p[1]/text()").extract()
        for i in ctac_address_list:
            if '联系人' in i:
                item['contact'] = i[i.index('：') + 1:]
            if '：' not in i:
                item['address'] = i
            # 解析网址信息
            item['website'] = response.xpath("//div[@class='detail_wrap']/p/a[@target]/text()").extract_first()
        return item


#启动以后的过程发生了什么？
# Scrapy为Spider的 start_urls 属性中的每个url创建了Request 对象，并将 parse 方法作为回调函数(callback)赋值给了requests
# ,而requests对象经过调度器的调度，执行生成response对象并送回给parse() 方法进行解析,所以请求链接的改变是靠回调函数实现的。
# yield scrapy.Request(self.url, callback=self.parse)


