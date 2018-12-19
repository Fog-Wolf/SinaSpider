#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: wang
# Date: 18/10/19 15:57

import re
from SinaSpider.tools.loghelper import Logger


def take_user_id(url):
    try:
        user_id = re.findall(r"^//weibo.com/(\d+)\?refer_flag", url)
        if user_id:
            return user_id[0]
        else:
            return 0
    except Exception as e:
        logs = Logger().logger
        user_id = 0
        return user_id


if __name__ == '__main__':
    res = take_user_id("https://weibo.com/sinahollyworld?refer_flag=1001030103_")
    print(res)
