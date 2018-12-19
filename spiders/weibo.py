# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from scrapy.http import Request
from urllib.parse import urljoin
from SinaSpider.items import SinaspiderItem, SinaspiderLoader
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from SinaSpider.tools import userid
from SinaSpider.tools import common
from datetime import datetime
from SinaSpider.tools.loghelper import Logger
import re


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com/']
    start_urls = ["https://s.weibo.com/"]

    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS": 5,
    }

    # 每个spider调用一个chrome，方便多线程处理
    def __init__(self):
        # 创建chrome参数对象
        opt = ChromeOptions()
        # 把chrome设置成无界面模式，不论windows还是linux都可以，自动适配对应参数
        opt.set_headless()
        # 创建chrome无界面对象
        self.brower = webdriver.Chrome(executable_path="D:/python/chromedriver.exe", options=opt)
        ## 有界面
        # self.brower = webdriver.Chrome(executable_path="D:/python/chromedriver.exe")
        # 设置加载页面超时时间
        self.brower.set_page_load_timeout(30)
        # 继承
        super(WeiboSpider, self).__init__()
        # 通过signals实现信号传递
        dispatcher.connect(self.spider_close, signals.spider_closed)

    def spider_close(self, spider):
        # 当爬虫关闭时，自动关闭chrome
        print("spider close")
        Logger().logger.debug("spider close")
        self.brower.quit()

    def parse(self, response):
        # 当前页面列表
        url_node = response.css(".m-main #pl_feed_main .m-wrap .m-con-l .card-wrap")
        for url in url_node:
            # 获取目标字段
            use_url = url.css(".card-feed .content .info .name::attr(href)").extract_first()
            if not use_url:
                Logger().logger.debug("no user url")
                continue
            user_id = userid.take_user_id(use_url)
            user_name = url.css(".card-feed .content .info .name::text").extract_first()
            user_image = url.css(".card-feed .avator img::attr(src)").extract_first()
            content_url = url.css(".card-feed .content .from a::attr(href)").extract_first()
            content = url.css(".card-feed .content .txt::text").extract()
            forward = common.get_num(url.css(".card-act li a::text").extract()[1])
            comment = common.get_num(url.css(".card-act li a::text").extract()[2])
            try:
                thumbsup = url.css(".card-act li a em::text").extract_first()
                if thumbsup is None:
                    raise Exception()
            except Exception as e:
                thumbsup = 0
            try:
                createdate = url.css(".card-feed .content .from a::text").extract()[0]
            except Exception as e:
                createdate = datetime.now()
            try:
                come_from = url.css(".card-feed .content .from a::text").extract()[1]
            except Exception as e:
                come_from = "微博 weibo.com"
            # 判断用户ID截取出来的是否是数字
            if user_id:
                url = "https://weibo.com/%s" % user_id
            else:
                url = "https:" + use_url
            # 访问
            yield Request(url=url,
                          meta={"content_url": content_url, "user_id": user_id, "user_image": user_image,
                                "user_name": user_name, "content": content,
                                "come_from": come_from, "createdate": createdate, "forward": forward,
                                "comment": comment, "thumbsup": thumbsup},
                          callback=self.parse_information,
                          dont_filter=True)
        # 提取下一页
        next_url = response.css(".m-page .next::attr(href)").extract_first()
        if next_url:
            Logger().logger.debug("next_url:" + next_url)
            yield Request(url=urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_information(self, response):
        item_loader = SinaspiderLoader(item=SinaspiderItem(), response=response)

        item_loader.add_value("user_url", response.url)
        item_loader.add_value("user_id", [response.meta.get("user_id", "")])
        item_loader.add_value("user_name", [response.meta.get("user_name", "")])
        item_loader.add_value("user_image", [response.meta.get("user_image", "")])
        item_loader.add_value("content", [response.meta.get("content", "")])
        item_loader.add_value("content_url", [response.meta.get("content_url", "")])
        item_loader.add_value("create_date", [response.meta.get("createdate", "")])
        item_loader.add_value("come_from", [response.meta.get("come_from", "")])
        item_loader.add_value("forward", [response.meta.get("forward", 0)])
        item_loader.add_value("comment", [response.meta.get("comment", 0)])
        item_loader.add_value("thumbsup", [response.meta.get("thumbsup", 0)])
        # 个人主页信息
        format = re.search('.*W_f(\d+).*', response.text)
        number_url = "#Pl_Core_T8CustomTriColumn__3 .S_line1 .W_f{0}::text".format(format.group(1))
        item_loader.add_css("weibo_number", number_url)
        # 储存
        article_item = item_loader.load_item()
        Logger().logger.debug(article_item)
        return article_item
