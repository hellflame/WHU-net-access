#!/usr/bin/env python
# coding=utf8
from sys import version_info
from re import compile
from config import username, password

if version_info.major == 2:
    from urllib2 import urlopen, URLError, Request, HTTPCookieProcessor, build_opener
    from cookielib import CookieJar
    from urllib import urlencode
    cookie = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie))
else:
    from urllib.request import urlopen, URLError, Request, HTTPCookieProcessor, build_opener
    from http import cookiejar
    from urllib.parse import urlencode
    cookie = cookiejar()
    opener = build_opener(HTTPCookieProcessor(cookie))

# this `try_url` does not require quit much but not https
try_url = 'http://www.baidu.com'


def downloader(url):
    try:
        handle = urlopen(url, timeout=3)
        return handle.read()
    except Exception:
        print 'Failed to retrieve the DATA !!'
        exit(1)


def get_auth_link():
    data = downloader(try_url)
    if not data.startswith('<script>'):
        print("You've already able to access the Network")
        exit(0)
    regs = compile(r"'(.+?)'")
    result = regs.findall(data)

    if not result or not result[0].startswith("http"):
        print("Failed the Retrieve Auth Page !!")
        exit(1)
    return result[0]


def do_login(auth_link, username, password, qr_code=''):
    opener.open(auth_link)
    post_data = {
        # 'usernameHidden': '',
        # 'username_tip': 'Username',
        'username': username,
        # 'strTypeAu': '',
        'uuidQrCode': qr_code,
        # 'authorMode': '',
        # 'pwd_tip': 'Password',
        'pwd': password
    }
    post_link = auth_link.replace("index.jsp?", 'userV2.do?method=login&')
    post_link += "&username={}&pwd={}".format(username, password)
    req = opener.open(post_link, urlencode(post_data))
    content = req.read()
    with open("result.html", 'w') as handle:
        handle.write(content)
    return content


def check_success(content):
    uname = compile("d.userName.innerText='(.+?)'").findall(content)
    userip = compile("d.contentDive.userip='(.+?)'").findall(content)
    time_left = compile("d.maxLeaving.innerText='(.+?)'").findall(content)
    account_left = compile("d.accountInfo.innerText='(.+?)'").findall(content)
    if not uname or not userip:
        print('Logging Failed......')
        return False
    else:
        print('Logging Succeeded')
        print('Username: {}'.format(uname[0]))
        print('IP: {}'.format(userip[0]))
        print("Time Left: {}".format(time_left[0].decode('gbk')))
        print("Account Remain: {}".format(account_left[0].decode('gbk')))
        return True


if __name__ == '__main__':
    auth_link = get_auth_link()
    check_success(do_login(auth_link, username, password))


