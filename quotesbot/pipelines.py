# 这里面贴出3种使用json格式保存提取的数据代码，只需要打开响应的注释即可使用，
# 每一种方式都有优化的地方，提供参考，最后使用了scrapy自身提供的json转换的方式，效率更高点
# 只要涉及到持久化相关的操作，必须写在管道文件中
# 注意：默认情况下管道机制并没有开启，需要手动在配置文件中手动开启
# import json
# class QsbkPipeline(object):
#     def __init__(self):
#         self.fp=open("duanzi.json",'w',encoding='utf-8')
#     def open_spider(self,spider):
#         print("爬虫开始了...")
#     def process_item(self, item, spider):
#         item_json=json.dumps(dict(item),ensure_ascii=False)
#         self.fp.write(item_json+'\n')
#         return item
#     def close_spider(self,spider):
#         self.fp.close()
#         print("爬虫结束了...")
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exporters import JsonItemExporter,JsonLinesItemExporter
import logging

# class QsbkPipeline(object):
#     def __init__(self):
#         self.fp=open("duanzi_v1.json",'wb')
#         self.exporter = JsonItemExporter(self.fp,ensure_ascii=False,encoding='utf-8')
#         self.exporter.start_exporting()
#
#     def open_spider(self,spider):
#         print("爬虫开始了...")
#
#     def process_item(self, item, spider):
#         self.exporter.export_item(item)
#         return item
#
#     def close_spider(self,spider):
#         self.exporter.finish_exporting()
#         self.fp.close()
#         print("爬虫结束了...")
import datetime
from quotesbot.items import EuserItem
from scrapy.utils.project import get_project_settings

class EuserPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        file_store = settings.get('FILE_STORE')
        to_day = datetime.datetime.now()
        file_name = r'euser_{}_{}_{}.json'.format(to_day.year, to_day.month, to_day.day)
        self.fp = open(file_store+file_name, 'wb')
        self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')

#只会被执行一次，spider开启时调用
    def open_spider(self, spider):
        logging.info("euser crawling start...")

#必须有，进行数据处理  item是spider生成的item 可以写入json文件，写入数据库，去重
#调用 爬虫每提交一次item 该方法被调用一次
#返回类型item，那么此Item会被低优先级的Item Pipeline的process_item()方法处理，直到所有的方法被调用完毕？
    def process_item(self, item, spider):
        if isinstance(item, EuserItem):#这是必要的吗？还是pipeline会自己去比对
            self.exporter.export_item(item)
            return item

#spider结束时调用
    def close_spider(self,spider):
        self.fp.close()
        logging.info("euser crawing finised...")

from quotesbot.items import GovBidItem
class GovBidPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        file_store = settings.get('FILE_STORE')
        to_day = datetime.datetime.now()
        file_name = r'govBidgk_{}_{}_{}.json'.format(to_day.year, to_day.month, to_day.day)
        self.fp = open(file_store + file_name, 'wb')
        self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')

    def open_spider(self, spider):
        logging.info("govBid gk crawling start...")


    def process_item(self, item, spider):
        if isinstance(item, GovBidItem):
            self.exporter.export_item(item)
            return item

    def close_spider(self,spider):
        self.fp.close()
        logging.info("govBid gk crawing finised...")


from quotesbot.items import GovBidXjItem
class GovBidXjPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        file_store = settings.get('FILE_STORE')
        to_day = datetime.datetime.now()
        file_name = r'govBidxj_{}_{}_{}.json'.format(to_day.year, to_day.month, to_day.day)
        self.fp = open(file_store + file_name, 'wb')
        self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')

    def open_spider(self, spider):
        logging.info("govBid xj crawling start...")


    def process_item(self, item, spider):
        if isinstance(item, GovBidXjItem):
            self.exporter.export_item(item)
            return item

    def close_spider(self,spider):
        self.fp.close()
        logging.info("govBidto xj crawing finised...")


from quotesbot.items import TianyanchaItem
class TianyanchaPipeline(object):
    def __init__(self):
        to_day = datetime.datetime.now()
        file_name = r'tianYanCha{}_{}_{}.json'.format(to_day.year, to_day.month, to_day.day)
        self.fp = open("C:/产品文档/爬虫-我的/" + file_name, 'wb')
        self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')

    def open_spider(self, spider):
        logging.info("tianYanCha crawling start...")


    def process_item(self, item, spider):
        if isinstance(item, TianyanchaItem):
            self.exporter.export_item(item)
            return item

    def close_spider(self,spider):
        self.fp.close()
        logging.info("tianYanCha crawing finised...")

import psycopg2 as pg
class PGPipeline(object):
    def open_spider(self, spider):
        hostname = '172.18.11.26'
        username = 'postgres'
        password = 'postgres_cnhis@#$'
        database = 'ai'
        # 创建连接
        self.conn = pg.connect(database=database, user=username, password=password, host=hostname, port="5432")
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            # self.conn.query(sql_desc)
            # cur.execute("INSERT INTO ewrrw values(dict(item));")
            self.cur.execute(
                """INSERT INTO tc_compete ("company_name","introduction","label","scale",
                "company_label","register_time","contact","telephone","phone","website","address") 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                (item["companyName"],
                    item["introduction"],
                    item["label"],
                    item["scale"],
                    item["comLabel"],
                    item["registerTime"],
                    item["contact"],
                    item["telephone"],
                    item["phone"],
                    item["website"],
                    item["address"]
                        ), )

            self.conn.commit()
            logging.msg("Data added to PostgreSQL database!",
                    level=logging.DEBUG, spider=spider)

        except Exception as e:
            logging.msg(e, level=logging.ERROR)
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
        logging.info("tianYanCha crawing finised...")