#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: wang
# Date: 18/11/14 10:39

from datetime import datetime
import time
import re


def time_date(date):
    if re.match('刚刚', date):
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())) + ':00'
    if re.match('\d+秒前', date):
        minute = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute))) + ':00'
    if re.match('\d+分钟前', date):
        minute = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60)) + ':00'
    if re.match('\d+小时前', date):
        hour = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60)) + ':00'
    if re.match('今天.*', date):
        date = re.match('今天(.*)', date).group(1).strip()
        date = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' ' + date + ':00'
    if re.match('昨天.*', date):
        date = re.match('昨天(.*)', date).group(1).strip()
        date = time.strftime('%Y-%m-%d', time.localtime(time.time() - float(24 * 60 * 60))) + ' ' + date + ':00'
    if re.match('\d{2}月\d{2}日', date):
        month = re.match('(\d+)月', date).group(1).strip()
        day = re.match('.*?(\d+)日', date).group(1).strip()
        hour = re.match(".*?(\d+):(\d+)", date).group(1).strip()
        min = re.match(".*?(\d+):(\d+)", date).group(2).strip()
        date = time.strftime('%Y-', time.localtime()) + month + '-' + day + ' ' + hour + ':' + min + ':00'
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # val = "2017年11月07日 13:50"
    # val = '今天14:15'
    # val = '20分钟前'
    # val = '2分钟前'
    val = '2秒前'
    # val = '11月12日 18:16'
    result = time_date(val)
    print(result)
