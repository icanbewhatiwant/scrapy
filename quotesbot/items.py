# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
#创建容器,不同信息放在不同容器中
# 定义item提前规划哪些字段需要抓取，scrapy.Field()仅是提前占坑
import scrapy
class EuserItem(scrapy.Item):
    # define the fields for your item here like:
    companyName = scrapy.Field()
    introduction =scrapy.Field()
    label = scrapy.Field()
    comLabel = scrapy.Field()
    scale = scrapy.Field()
    registerTime = scrapy.Field()
    contact = scrapy.Field()
    telephone = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    address = scrapy.Field()

class GovBidItem(scrapy.Item):
    """
    19个
    projectName ：采购项目名称
    pingmu ：品目
    purUnit ：采购单位
    adminiArea ：行政区域
    bulletTime ：公告时间
    obtBidTime ：获取招标文件时间
    bidDocPrice：招标文件售价
    obtBidLoc ：获取招标文件地点
    staBidTime ：开标时间
    staLoc ：开标地点
    budget ：预算金额
    proContact ：项目联系人
    proPhone ：项目联系电话
    purAddress ：采购单位地址
    purUnitPhone ：采购单位联系方式
    agentName ：代理结构名称
    agentAddress ：代理机构地址
    agentPhone ：代理机构联系方式
    appendix ：附件，分号分隔，用字符串的形式拼接，可能多个
    """
    projectName = scrapy.Field()
    pingmu = scrapy.Field()
    purUnit = scrapy.Field()
    adminiArea = scrapy.Field()
    bulletTime = scrapy.Field()
    obtBidTime = scrapy.Field()
    bidDocPrice = scrapy.Field()
    obtBidLoc = scrapy.Field()
    staBidTime = scrapy.Field()
    staLoc = scrapy.Field()
    budget = scrapy.Field()
    proContact = scrapy.Field()
    proPhone = scrapy.Field()
    purAddress = scrapy.Field()
    purUnitPhone =scrapy.Field()
    agentName =scrapy.Field()
    agentAddress = scrapy.Field()
    agentPhone = scrapy.Field()
    appendix = scrapy.Field()

class GovBidXjItem(scrapy.Item):
    """
        projectName ：采购项目名称
        pingmu ：品目
        purUnit ：采购单位
        adminiArea ：行政区域
        bulletTime ：公告时间
        obtBidTime ：获取采购文件时间
        budget ：预算金额
        proContact ：项目联系人
        proPhone ：项目联系电话
        purAddress ：采购单位地址
        purUnitPhone ：采购单位联系方式
        agentName ：代理结构名称
        agentAddress ：代理机构地址
        agentPhone ：代理机构联系方式
        appendix ：附件，分号分隔，用字符串的形式拼接，可能多个
    """
    projectName = scrapy.Field()
    pingmu = scrapy.Field()
    purUnit = scrapy.Field()
    adminiArea = scrapy.Field()
    bulletTime = scrapy.Field()
    obtBidTime = scrapy.Field()
    bidDocPrice = scrapy.Field()
    obtBidLoc = scrapy.Field()
    staBidTime = scrapy.Field()
    staLoc = scrapy.Field()
    budget = scrapy.Field()
    proContact = scrapy.Field()
    proPhone = scrapy.Field()
    purAddress = scrapy.Field()
    purUnitPhone = scrapy.Field()
    agentName = scrapy.Field()
    agentAddress = scrapy.Field()
    agentPhone = scrapy.Field()
    appendix = scrapy.Field()


class TianyanchaItem(scrapy.Item):
    compName = scrapy.Field() #公司名称
    label = scrapy.Field() #标签：妇科、产科、儿科、骨科、皮肤科、眼科、美容、体检、康复、养老、口腔、肿瘤
    regisCapital = scrapy.Field() #注册资本
    establishDate = scrapy.Field() #成立日期
    UniSociCreCode = scrapy.Field() #统一社会信用代码
    taxpIdentity = scrapy.Field() #纳税人识别号
    compType = scrapy.Field() #公司类型
    busiTerm = scrapy.Field() #营业期限
    staffSize = scrapy.Field() #人员规模
    regisAdress = scrapy.Field() #注册地址
    busiScope = scrapy.Field() #经营范围
    busiState = scrapy.Field() #经营状态
    industry = scrapy.Field() #行业



















