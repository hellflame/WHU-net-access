#!/usr/bin/env python
# coding=utf8

from sys import version_info, platform, argv
from re import compile
import json

if version_info.major == 2:
    from urllib2 import urlopen, URLError, Request, HTTPCookieProcessor, build_opener
    from cookielib import CookieJar
    from urllib import urlencode
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    cookie = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie))
else:
    from urllib.request import urlopen, URLError, Request, HTTPCookieProcessor, build_opener
    from http.cookiejar import CookieJar
    from urllib.parse import urlencode
    cookie = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie))

# this `try_url` does not require quit much but not https
try_url = 'http://www.baidu.com'


def downloader(url):
    try:
        handle = urlopen(url, timeout=3)
        return handle.read()
    except Exception:
        print('Failed to retrieve the DATA !!')
        exit(1)


def get_auth_link():
    data = downloader(try_url)
    if not data.startswith(b'<script>'):
        print("You've already able to access the Network")
        exit(0)
    regs = compile(b"'(.+?)'")
    result = regs.findall(data)

    if not result or not result[0].startswith(b"http"):
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
        if 'linux' in platform:
            print('Logging \033[01;31mSucceeded\033[00m!!\n')
            print('Username: \033[01;34m{}\033[00m'.format(uname[0]))
            print('IP: \033[01;37m{}\033[00m'.format(userip[0]))
            print("Time Left: \033[01;32m{}\033[00m".format(time_left[0].decode('gbk')))
            print("Account Remain: \033[01;31m{}\033[00m\n".format(account_left[0].decode('gbk')))
        else:
            print('Logging Succeeded')
            print('Username: {}'.format(uname[0]))
            print('IP: {}'.format(userip[0]))
            print("Time Left: {}".format(time_left[0]))
            print("Account Remain: {}".format(account_left[0]))
        return True


def help_menu():
    """
    ===* net-access-whu help menu *===

     -u     username
     -p     password
     -c     config file

     deploy like this:
        method 1. net-access-whu -u your_account -p your_password
        method 2. net-access-whu -c config.json

        config.json has the format like below:
            {
                "username": "your_account",
                "password": "your_password"
            }
    """
    print(help_menu.__doc__)


def main():
    if not len(argv) == 3 and not len(argv) == 5:
        return help_menu()
    username = ''
    password = ''
    for i in argv[1:]:
        if i == '-c':
            with open(argv[argv.index(i) + 1]) as handle:
                reader = handle.read()
            try:
                reader = json.loads(reader)
            except Exception as e:
                print(e)
                return help_menu()
            username = reader.get("username", '')
            password = reader.get("password", '')
            break
        if i == '-u':
            username = argv[argv.index(i) + 1]
        if i == '-p':
            password = argv[argv.index(i) + 1]
    auth_link = get_auth_link()
    check_success(do_login(auth_link, username, password))

if __name__ == '__main__':
    main()
