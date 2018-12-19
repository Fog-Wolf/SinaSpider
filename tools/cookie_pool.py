#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: wang
# Date: 18/10/24 18:20
import requests, json, re, os
import base64
import rsa, binascii
import logging
import time
import random

usernamelist = {'13120951901': '951017han', '18255388259': '24tidy!', '13673311501': '5616132qq',
                '17754034953': 'miguquanquan2018'}
set_get_login = "https://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=MTcxNjYxMDM0ODQ%3D&rsakt=mod&client=ssologin.js(v1.4.15)&_=1501138087057"
set_post_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=1501138087464"
date = time.strftime('%Y-%m-%d', time.localtime())


def weibo_cookie():
    url = requests.get(set_get_login)
    if url.status_code == 200:
        json_data = re.findall(r"^sinaSSOController.preloginCallBack\((.*)\)", url.text)[0]
        data = json.loads(json_data)
        servertime = data["servertime"]
        nonce = data["nonce"]
        pubkey = data["pubkey"]
        rsakv = data["rsakv"]
        for username in usernamelist.keys():
            print(username + "Start Login")
            su = base64.b64encode(username.encode(encoding='utf-8'))
            rsaPublickey = int(pubkey, 16)
            key = rsa.PublicKey(rsaPublickey, 65537)
            message = str(servertime) + '\t' + str(nonce) + '\n' + str(usernamelist.get(username))
            sp = binascii.b2a_hex(rsa.encrypt(message.encode(encoding='utf-8'), key))
            post_data = {
                'entry': 'sso',
                'geteway': '1',
                'from': 'null',
                'savestate': '30',
                'userticket': '0',
                'vsnf': '1',
                'su': su,
                'service': 'sso',
                'servertime': servertime,
                'nonce': nonce,
                'pwencode': 'rsa2',
                'sp': sp,
                'encoding': 'UTF-8',
                'returntype': 'TEXT',
                'rsakv': rsakv,
                'pagerefer': 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)',
                'cdult': '3',
                'domain': 'sina.com.cn',
                'prelt': '24'
            }
            session = requests.session()
            resp = session.post(set_post_url, data=post_data, verify=False)
            if resp.status_code == 200:
                try:
                    URL = re.search(r'(https\:.*?)"', resp.text).group(1).replace('\\', '')
                except Exception as e:
                    pass
                result = session.get(URL)
                logging.info(result)
                cookies = json.dumps(session.cookies.get_dict()).replace('\'', '"')
                with open(os.path.join(os.path.abspath('..'), 'pool\cookies', username + '_' + date + '.txt'),
                          "w+") as w:
                    w.writelines(cookies)
            else:
                logging.error("Request login failed！" + resp.status_code)
                return "Request login failed！"
            print(username + "Login success")
            time.sleep(3)
    else:
        logging.error("Link access error！" + url.status_code)
        return "Link access error！"


class getCookie(object):
    def get_random_cookie(self):
        username = random.choice(list(usernamelist))
        result = ''
        try:
            url = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pool\cookies',
                               username + '_' + date + '.txt')
            with open(url) as f:
                data = f.read()
                data = json.loads(data)
                for key, value in data.items():
                    result += key + ":" + value + ";"
            if not result.strip():
                self.get_random_cookie()
        except Exception as e:
            cookie = weibo_cookie()
            if cookie:
                self.get_random_cookie()
            else:
                print('Worry:' + e)
        else:
            return result


if __name__ == "__main__":
    result = weibo_cookie()
    print(result)
