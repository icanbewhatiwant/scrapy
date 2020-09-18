import scrapy
# scrapy 信号相关库
from scrapy import signals
from pydispatch import dispatcher
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

import time
import re
import requests
from io import BytesIO
from PIL import Image
import random
from quotesbot.items import TianyanchaItem

class TianYanSpider(scrapy.Spider):
    name = 'tianyancha'
    allowed_domains = ['tianyancha.com/','https://www.tianyancha.com/']
    user ="13590170246"
    pwd ="zuobiao888"
    label_list = ["妇科","产科","儿科","骨科","皮肤科","眼科","美容","体检","康复","养老","口腔","肿瘤"]


    # 将chrome初始化放到spider中，成为spider中的元素
    def __init__(self):
        self.driver = webdriver.Chrome(r"C:\软件\chromedriver_win32\chromedriver.exe")
        self.wait = WebDriverWait(self.driver, 100)
        super().__init__()  # 调用父类方法
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.TianYanSpiderCloseHandle,
                           signal=signals.spider_closed
                           )

    # 信号量处理函数：关闭chrome浏览器
    def TianYanSpiderCloseHandle(self, spider):
        print(f"TianYanSpiderCloseHandle: enter ")
        self.driver.quit()

    start_urls = [
        'https://www.tianyancha.com/',
        # 'https://www.tianyancha.com/search/ocQ-s1?key=医院',
    ]

    def start_requests(self):
        # 把所有的URL地址统一扔给调度器入队列
        url = 'https://www.tianyancha.com/'
        self.driver.get(url)
        # 交给调度器
    #     yield scrapy.Request(
    #         url=url,
    #         callback=self.parse
    #     )
    #
    # def parse(self,response):
        time.sleep(2)
        #点击登录模块 login_button点击弹出登录框 button2点击跳转到密码登录界面 输入账户密码 点击登录跳出验证码框
        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='link-white']")))
        login_button.click()
        button2 = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="title-tab text-center"]/descendant::div[2]')))
        button2.click()
        # 账号密码登录框
        time.sleep(2)
        input_user = self.driver.find_element_by_xpath('//input[@id="mobile"]').clear()
        input_psw = self.driver.find_element_by_xpath('//input[@id="password"]').clear()
        self.driver.find_element_by_xpath('//input[@id="mobile"]').send_keys(self.user)  # 发送登录账号
        self.driver.find_element_by_xpath('//input[@id="password"]').send_keys(self.pwd)
        time.sleep(2)  # 等待 一秒 方式被识别为机器人
        login = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="sign-in"]/div[2]/div[2]')))
        login.click()

        #处理验证码模块
        # self.autologin()
        time.sleep(10)
        try:
            # 拖动的滑块
            if self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]'):
                print('能找到滑块，重新试')
                # self.driver.delete_all_cookies()
                # self.driver.refresh()
                # self.start_requests()
            else:
                print('login success, slider missing!')
        except:
            print('login success')

        #爬取数据
        yield scrapy.Request(url='https://www.tianyancha.com/search/ocQ-s1?key=医院',
                            callback=self.parse_next_page,
                              dont_filter=True)

    def parse_next_page(self,response):
        # 本页信息列表urls处理
        for titUrl in response.xpath("//div[@class='content']/div[@class='header']/a"):
            url = titUrl.xpath("./@href").extract()[0]
            # title = titUrl.xpath("string(.)").extract()[0]
            # title = title.strip()
            yield scrapy.Request(url=url,
                                callback=self.parse_detail)

        # 获取next_page_url发送氢请求
        try:
            next_url = response.xpath("//a[@class='num -next']/@href").extract_first()
            if next_url != "" and next_url is not None:
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
        item["compName"] = response.xpath("string(//h1[@class='name'])").extract_first()
        for l in self.label_list:
            if l in item["compName"]:
                label.append(l)
        if len(label)>=1:
            labelStr = ','.join(label)
        item["label"] = labelStr

        table = response.xpath("//table[@class='table -striped-col -border-top-none -breakall']/tbody")
        item["regisCapital"] = table.xpath("string(//tr[1]/td[2])").extract_first()
        item["establishDate"] = response.xpath("string(//tr[2]/td[2])").extract_first()
        item["UniSociCreCode"] = response.xpath("string(//tr[3]/td[2])").extract_first()
        item["taxpIdentity"] = response.xpath("string(//tr[4]/td[2])").extract_first()
        item["compType"] = response.xpath("string(//tr[5]/td[2])").extract_first()
        item["busiTerm"] = response.xpath("string(//tr[7]/td[2])").extract_first()
        item["staffSize"] = response.xpath("string(//tr[8]/td[2])").extract_first()
        item["regisAdress"] = response.xpath("string(tr[10]/td[2])").extract_first()
        item["busiScope"] = response.xpath("string(//tr[11]/td[2])").extract_first()
        item["busiState"] = response.xpath("string(tr[2]/td[4])").extract_first()
        item["industry"] = response.xpath("string(tr[5]/td[4])").extract_first()
        return item

        custom_settings = {
            "RANDOM_DELAY": 5,
            "DOWNLOADER_MIDDLEWARES": {
                'quotesbot.middlewares.TyanSelMiddleware': 543,
                # 将scrapy默认的user-agent中间件关闭
                'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None

            },
            'ITEM_PIPELINES': {'quotesbot.pipelines.TianyanchaPipeline': 300, }
        }

    #验证码模块
    def autologin(self):
        time.sleep(2)
        gap_image_position, nogap_image_position, gap_image_url, nogap_image_url = self.get_image_info()
        new_gapimage, new_nogapimage = self.get_image_complete(gap_image_position, nogap_image_position, gap_image_url,
                                                               nogap_image_url)
        distance = self.get_move_distance(new_gapimage, new_nogapimage)
        self.slid_button(distance)

    # 获得图片的拼接列表，以及列表的位置信息 用于后面还原图片
    def get_image_info(self):
        """
        获得图片的信息，如图片的url，图片的坐标信息。
        共获得两份图片，一份是有缺口的，一份没有缺口。
        :return: gap_image_list和nogap_image_list图片是一系列的div拼接起来的
        """
        gap_image_list = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gt_cut_bg_slice"]')))
        # '//div[@class="user-login-box"]//div[@class="gt_cut_bg gt_show"]/div[@class="gt_cut_bg_slice"]')))
        nogap_image_list = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gt_cut_fullbg_slice"]')))
        # 获取url地址                                                                      # '//div[@class="user-login-box"]//div[@class="gt_cut_fullbg gt_show"]/div[@class="gt_cut_fullbg_slice"]')))
        gap_image_url = re.findall(r'url\("(.*?)"\)', gap_image_list[0].get_attribute('style'))[0]
        nogap_image_url = re.findall(r'url\("(.*?)"\)', nogap_image_list[0].get_attribute('style'))[0]

        # 返回所有图片的位置信息 list
        gap_image_position = [re.findall(r'background-position: -(.*?)px -?(.*?)px;', i.get_attribute('style'))[0] for i
                              in gap_image_list]
        nogap_image_position = [re.findall(r'background-position: -(.*?)px -?(.*?)px;', i.get_attribute('style'))[0] for
                                i in nogap_image_list]
        return gap_image_position, nogap_image_position, gap_image_url, nogap_image_url

    #还原混乱的图片
    def get_image_complete(self, gap_image_position, nogap_image_position, gap_image_url, nogap_image_url):
        """
        将获得混乱的图片，用获得的信息，拼接成正常的图片。
        :param gap_image_position:
        :param nogap_image_position:
        :param gap_image_url:
        :param nogap_image_url:
        :return:
        """
        # BytesIO实现了在内存中读写bytes，我们创建一个BytesIO，然后写入一些bytes
        gap_image_file = BytesIO(requests.get(gap_image_url).content)
        nogap_image_file = BytesIO(requests.get(nogap_image_url).content)
        old_gapimage = Image.open(gap_image_file)  # 专接图片路径
        new_gapimage = Image.new('RGB', (260, 116))  # 拼接图片：58*10 长宽 两行26列 所以新建图片宽26*10 长58*2
        old_nogapimage = Image.open(nogap_image_file)
        new_nogapimage = Image.new('RGB', (260, 116))
        up_count = 0
        down_count = 0
        # 拼接缺口图片  gap_image_position：52个 分为上下两部分 如：-157px -58px（左上顶点） 下部分存在：-157px 0px
        #   其中-58px与0px固定 前面数字上下部分重复并变化
        for i in gap_image_position[:26]:
            # 切割图像 粘贴还原下半部分图片
            cut_image = old_gapimage.crop((int(i[0]), 58, int(i[0]) + 10, 116))  # 左上顶点 右下顶点坐标
            new_gapimage.paste(cut_image, (up_count, 0))
            up_count = up_count + 10  # 图片就是260 粘贴26次
        for i in gap_image_position[26:]:  # 粘贴还原上半部分图片
            cut_image = old_gapimage.crop((int(i[0]), 0, int(i[0]) + 10, 58))  # 左上顶点，右下顶点
            new_gapimage.paste(cut_image, (down_count, 58))
            down_count = down_count + 10
        # 拼接无缺口图片
        up_count = 0
        down_count = 0
        for i in nogap_image_position[:26]:
            cut_image = old_nogapimage.crop((int(i[0]), 58, int(i[0]) + 10, 116))  # 左上顶点，右下顶点
            new_nogapimage.paste(cut_image, (up_count, 0))
            up_count = up_count + 10
        for i in gap_image_position[26:]:
            cut_image = old_nogapimage.crop((int(i[0]), 0, int(i[0]) + 10, 58))  # 左上顶点，右下顶点
            new_nogapimage.paste(cut_image, (down_count, 58))
            down_count = down_count + 10
        return new_gapimage, new_nogapimage

    # 获取滑动距离
    def get_move_distance(self, new_gapimage, new_nogapimage):
        def compare_image(p1, p2):
            """
            比较图片的像素
            由于RGB图片一个像素点是三维的，所以循环三次
            算法是两个图层里相同位置的每个像素点RGB值的差
            :return:
            """
            for i in range(3):
                if abs(p1[i] - p2[i]) >= 50:
                    return False
                return True

        for i in range(260):  # 返回i就是距离
            for j in range(116):
                # 获取图像中某一点的像素的RGB颜色值，参数是一个坐标点。对于图象的不同的模式，getpixel函数返回的值有所不同。
                gap_pixel = new_gapimage.getpixel((i, j))
                nogap_pixel = new_nogapimage.getpixel((i, j))
                if not compare_image(gap_pixel, nogap_pixel):
                    return i

    #滑动验证码
    def slid_button(self, distance):
        # 获取滑块元素
        button = self.driver.find_element_by_xpath(
            '//div[@class="gt_slider_knob gt_show"]')
        # '//div[@class="user-login-box"]//div[@class="gt_slider_knob gt_show"]')
        ActionChains(self.driver).click_and_hold(button).perform()
        time.sleep(0.5)
        track_list = self.track(distance - 3)
        # print(track_list)
        for i in track_list:
            ActionChains(self.driver).move_by_offset(i, 0).perform()
        time.sleep(1)
        ActionChains(self.driver).release().perform()
        time.sleep(2)
        try:
            #拖动的滑块
            if self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]'):
                print('能找到滑块，重新试')
                self.driver.delete_all_cookies()
                self.driver.refresh()
                self.start_requests()
            else:
                print('login success, slider missing!')
        except:
            print('login success')

    #获取滑动轨迹
    def track(self, distance):
        # t = 0.1
        # speed = 0
        # current = 0
        # 减速阈值
        # mid = 3 / 5 * distance
        t = 0.2
        speed = 1
        current = 0
        mid = 2 / 5 * distance
        track_list = []
        while current < distance:
            if current < mid:
                # a = random.choice([1, 2, 3])
                a = 5
            else:
                a = -2
            move_track = speed * t + 0.5 * a * t ** 2
            track_list.append(round(move_track))
            speed = speed + a * t
            current += move_track
        # 模拟人类来回移动了一小段
        end_track = [1, 0] * 10 + [0] * 10 + [-1, 0] * 10
        track_list.extend(end_track)
        offset = sum(track_list) - distance
        # 由于四舍五入带来的误差,这里需要补回来
        if offset > 0:
            track_list.extend(offset * [-1, 0])
        elif offset < 0:
            track_list.extend(offset * [1, 0])
        return track_list



