#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: wang
# Date: 18/11/20 17:26
from scrapy.cmdline import execute
import os, sys
import re
import pymysql

conn = pymysql.connect("localhost", "root", "root", "sina", charset='utf8', use_unicode=True)
cursor = conn.cursor()


# 重启程序
def restart_program():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", "weibo"])


# 提取数字
def get_num(content):
    try:
        number = re.findall(r"\d+", content)
        return number[0]
    except Exception as e:
        number = 0
        return number


def keywordsSearch():
    key = ''
    sql = """
                SELECT * FROM `spider_keywords` 
                WHERE `status`=0
                ORDER BY RAND()
                LIMIT 1;
        """
    num = cursor.execute(sql)
    if num > 0:
        results = cursor.fetchall()
        for res in results:
            id = res[0]
            key = res[1]
            update_sql = """
                           UPDATE spider_keywords SET `status`=1 WHERE `id`={0};
                    """.format(id)
            cursor.execute(update_sql)
            conn.commit()
        return key
    else:
        update_sql = """
               UPDATE spider_keywords SET `status`=0 WHERE `status`=1;
        """
        cursor.execute(update_sql)
        conn.commit()
        return keywordsSearch()


def weibo_num_list_to_dic(value):
    keys = ['follow_num', 'fan_num', 'weibo_num']
    result = dict(zip(keys, value))
    return result


if __name__ == "__main__":
    result = weibo_num_list_to_dic([123, 134, 142])
    print(result["follow_num"])
