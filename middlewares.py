# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from SinaSpider.user_agents import agents
from scrapy.http import HtmlResponse
from SinaSpider.settings import KEYWORDS
from SinaSpider.tools.crawl_xici_ip import GetIP
from SinaSpider.tools.cookie_pool import getCookie
from SinaSpider.tools.loghelper import Logger
from selenium.common.exceptions import TimeoutException
from scrapy.xlib.pydispatch import dispatcher


class SinaspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandUserAgentMiddleware(object):
    # 换User-Agent
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    def process_request(self, request, spider):
        get_cookie = getCookie()
        request.headers["Cookies"] = get_cookie.get_random_cookie()
        # print(request.headers["Cookies"])


class RandomProxyMiddleware(object):
    # 动态设置ip代理
    def process_request(self, request, spider):
        get_ip = GetIP()
        request.meta["proxy"] = get_ip.get_random_ip()
        # print(request.meta["proxy"])


class JSPageMiddleware(object):
    def __init__(self):
        self.logger = Logger().logger

    # 通过chrome请求动态网页
    def process_request(self, request, spider):
        import re, time
        start_time = time.clock()
        try:
            spider.brower.get(request.url)
        except TimeoutException:
            # 加载超时
            self.logger.debug('The first time out after 30 seconds when loading page! ' + request.url)
            # 再次请求
            try:
                spider.brower.set_page_load_timeout(100)
                spider.brower.get(request.url)
            except TimeoutException:
                # 加载超时停止爬去
                self.logger.debug('The second time out after 100 seconds when loading page ' + request.url)
                return dispatcher.connect(spider.spider_close, signals.spider_closed)
        finally:
            end_time = time.clock()
            # 计算并记录执行访问的时间
            post_time = end_time - start_time
            self.logger.debug(request.url + " runtime:" + str(post_time))
        # 搜索按钮控制
        if re.match("/?(.*s.weibo.com/)$", request.url):
            print(KEYWORDS)
            self.logger.debug("keyword:{0}".format(KEYWORDS))
            try:
                spider.brower.find_element_by_xpath("//*[@id='pl_homepage_search']/div/div[2]/div/input").send_keys(
                    KEYWORDS)
                spider.brower.find_element_by_css_selector(".s-btn-b").click()
            except Exception as e:
                print(e)
                return dispatcher.connect(spider.spider_close, signals.spider_closed)
        print("Visit:{0}".format(request.url))
        self.logger.debug("Visit:{0}".format(request.url))
        time.sleep(10)
        if spider.brower.current_url == 'https://weibo.com/login.php':
            self.logger.debug("Crawl failure, restart the crawler after 60 seconds!")
            return dispatcher.connect(spider.spider_close, signals.spider_closed)
        # 通过HtmlResponse跳过下载器下载页面动作
        return HtmlResponse(url=spider.brower.current_url, body=spider.brower.page_source, encoding='utf-8',
                            request=request)
