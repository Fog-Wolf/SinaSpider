# -*- coding: utf-8 -*-
__author__ = 'bobby'
import requests
import pymysql
import sys, os, json

conn = pymysql.connect("localhost", "root", "root", "sina", charset='utf8', use_unicode=True)
cursor = conn.cursor()


def crawl_ips():
    # 请求西刺的免费ip代理接口
    re = requests.get("https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list")
    if re.status_code == 200:
        with open(os.path.join(os.path.abspath('..'), 'pool', 'xici.txt'), "w+") as w:
            w.writelines(re.text)
    else:
        exit("Request error:" + re.status_code)
    f = open(os.path.join(os.path.abspath('..'), 'pool', 'xici.txt'), "r")
    content = f.readlines()

    for ip_info in content:
        ip_info = json.loads(ip_info)
        if int(ip_info["response_time"]) >= 5.00 or ip_info["type"] == 'http' or ip_info["anonymity"] != 'high_anonymous':
            continue
        insert_sql = """
                        INSERT INTO proxy_ip(`ip`,`port`,`speed`,`proxy_type`,`come_from`,`country`) VALUES ("{0}","{1}","{2}","{3}","{4}","{5}");
                    """.format(ip_info["host"], ip_info["port"], ip_info["response_time"], ip_info["type"],
                               ip_info["from"],
                               ip_info["country"])
        try:
            cursor.execute(insert_sql)
            conn.commit()
        except Exception as e:
            print(e)
            continue
    return "Success"


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "https://www.baidu.com"
        proxy_url = "https://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        random_sql = """
              SELECT ip, port FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
            """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "https://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


# print (crawl_ips())
if __name__ == "__main__":
    clean_sql = """
                    TRUNCATE TABLE proxy_ip;
                """
    cursor.execute(clean_sql)
    conn.commit()
    crawl_ips()
