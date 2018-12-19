# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from SinaSpider.settings import SQL_DATE_TIME_FORMAT
from SinaSpider.tools.formatting_time import time_date
from SinaSpider.settings import KEYWORDS
from SinaSpider.tools import common
from SinaSpider.tools.loghelper import Logger


class SinaspiderLoader(ItemLoader):
    default_output_processor = TakeFirst()
    pass


def clean_strip(value):
    # 清除空格和换行符
    res = ''
    for v in value:
        res = (v.replace("\n", "")).strip()
    return res


def add_http(value):
    # 添加地址前缀
    value = "https:" + value
    return value


def change_time(value):
    value = value.replace('\n', '').strip()
    value = time_date(value)
    return value


def str_data(value):
    return value


class SinaspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_url = scrapy.Field(
        output_processor=MapCompose(str_data),
    )
    user_name = scrapy.Field()
    user_image = scrapy.Field(
        input_processor=MapCompose(add_http),
    )
    user_id = scrapy.Field()
    content_url = scrapy.Field(
        input_processor=MapCompose(add_http),
    )
    content = scrapy.Field(
        input_processor=MapCompose(clean_strip),
        output_processor=Join(","),
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(change_time),
    )
    come_from = scrapy.Field()
    forward = scrapy.Field()
    comment = scrapy.Field()
    thumbsup = scrapy.Field()
    weibo_number = scrapy.Field(
        output_processor=MapCompose(str_data),
    )

    def get_insert_sql(self):
        # sql = "INSERT INTO app_scrapydata(user_url,user_name,user_image,user_id,content_url,content,follow_num,fan_num,weibo_num,come_from,keywords,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE follow_num=%s,fan_num=%s,weibo_num=%s;"
        sql = "INSERT INTO sina_weibo(user_url,user_name,user_image,user_id,content_url,content,follow_num,fan_num,weibo_num,forward,comment,thumbsup,come_from,keywords,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE follow_num=%s,fan_num=%s,weibo_num=%s,forward=%s,comment=%s,thumbsup=%s;"
        number = common.weibo_num_list_to_dic(self["weibo_number"])
        if 'thumbsup' not in self:
            self['thumbsup'] = 0
        params = (
            self["user_url"][0], self['user_name'], self['user_image'], self["user_id"], self["content_url"],
            self['content'], number["follow_num"],
            number['fan_num'],
            number['weibo_num'], self['forward'], self['comment'], self['thumbsup'], self['come_from'], KEYWORDS,
            self['create_date'].strftime(SQL_DATE_TIME_FORMAT),
            number['follow_num'], number['fan_num'], number['weibo_num'], self['forward'], self['comment'],
            self['thumbsup'])
        Logger().logger.debug(params)
        return sql, params
