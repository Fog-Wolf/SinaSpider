# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.connections
import pymysql.cursors
from twisted.enterprise import adbapi
from SinaSpider.tools.loghelper import Logger


class SinaspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    # 采用异步的方式写入MYSQL
    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USERNAME"],
            passwd=settings["MYSQL_PASSWORD"],
            port=settings["MYSQL_PORT"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        # 异步链接池
        dbpool = adbapi.ConnectionPool("pymysql", **dbparams)
        return cls(dbpool)

    def __init__(self, dbpool):
        self.dbpool = dbpool

    def process_item(self, item, spider):
        # 使用twisted将MySQL插入变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        Logger().logger.error(item)
        Logger().logger.error('--------- error ---------')
        Logger().logger.error(failure)

    def do_insert(self, cursor, item):
        # 根据不同的ITEM 构建不同的sql语句并插入数据库中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
