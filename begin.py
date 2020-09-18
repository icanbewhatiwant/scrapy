from scrapy import cmdline
import sys,time,os
#
# #医信邦
# # cmdline.execute("scrapy crawl euser".split())
#
# #政府采购网 公开信息
# cmdline.execute("scrapy crawl seleniumSpider".split())
# 政府采购网 公开招标三个月信息
# cmdline.execute("scrapy crawl threeMonthGk".split())
# #政府采购网 询价公告昨日数据
cmdline.execute("scrapy crawl govBidxj".split())
# 政府采购网 询价公告三个月数据
# cmdline.execute("scrapy crawl ThreeMonXj".split())
# cmdline.execute("scrapy crawl tests".split())
#gk特定页面详情
# cmdline.execute("scrapy crawl gvgkdetailSpider".split())

# ------------------------------------------------------

from scrapy import cmdline
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from quotesbot.spiders.govmentBid import GovmentBid
from quotesbot.spiders.seleniumSpider import SeleniumSpider
from scrapy.utils.project import get_project_settings

'''
以下是多个爬虫顺序执行的命令
'''
# configure_logging()
# # 加入setting配置文件，否则配置无法生效
# # get_project_settings()获取的是setting.py的配置
# runner = CrawlerRunner(get_project_settings())
#
# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(GovmentBid)
#     yield runner.crawl(SeleniumSpider)
#     reactor.stop()
#
# crawl()
# reactor.run()  # the script will block here until the last crawl call is finished







