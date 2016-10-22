#!/usr/bin/env python
# coding=utf8

from sys import platform, argv
from re import compile, DOTALL
import json
import tempfile
import os

from urllib2 import urlopen, HTTPCookieProcessor, build_opener
from cookielib import CookieJar
from urllib import urlencode
import sys
reload(sys)
sys.setdefaultencoding('utf8')
cookie = CookieJar()
opener = build_opener(HTTPCookieProcessor(cookie))


# this `try_url` does not require quit much but not https, better with no redirection
try_url = 'http://www.baidu.com'

# ip and port of the url
ip_port = ''


def downloader(url):
    try:
        handle = urlopen(url, timeout=5)
        return str(handle.read()), handle.url
    except Exception as e:
        print(e)
        print('Failed to retrieve the DATA !!')
        exit(1)


def logout(uname):
    if not uname:
        print("Username is necessary no matter who you are!!")
        return False
    temp_file = tempfile.gettempdir() + "/{}-whu.logout".format(uname)
    iis_temp = tempfile.gettempdir() + "/IIS-WEB.logout"
    if not os.path.exists(temp_file) and not os.path.exists(iis_temp):
        print("You've NOT Login Yet!!!")
        exit(1)
    if os.path.exists(temp_file):
        with open(temp_file) as handle:
            content = handle.read()
            mode = 'WHU'
    else:
        with open(iis_temp) as handle:
            content = handle.read()
            mode = "IIS"

    if not content:
        print("You've Logout already ~~")
        exit(0)

    feed, url = downloader(content)

    if mode == 'WHU':

        regs = compile("""window.location.replace\("(.+?)"\)""", DOTALL)
        match = regs.findall(feed)
        if match and 'goToLogout' in match[0]:
            print("Logout Succeeded!")
            os.unlink(temp_file)
            return True
        print("Logout Failed!")
        return False
    else:
        data_str = content.split("?")[-1]
        req = opener.open(url, data=data_str)
        result = req.read()
        error_code = compile("<errcode>(.+?)</errcode>").findall(result)
        msg = compile("<message>(.+?)</message>").findall(result)
        if int(error_code[0]) == 0:
            print("Logout Succeeded!")
            os.unlink(iis_temp)
            return True
        else:
            print("Logout Failed......")
            print(msg[0].strip())
            return False


def get_auth_link():
    data, url = downloader(try_url)

    if url == try_url and not data.startswith("<script>") or url != try_url:
        print("You've already able to access the Network")
        exit(0)

    if 'Portal登陆页面' in data:
        return url, 'IIS'

    regs = compile("'(.+?)'")
    result = regs.findall(data)

    if result and result[0].startswith("http"):
        return result[0], 'COMMON'
    else:
        print("Failed the Retrieve Auth Page !!")
        exit(1)


def do_login(auth_link, username, password, qr_code=''):
    post_data = {
        'username': username,
        'uuidQrCode': qr_code,
        'pwd': password
    }
    post_link = auth_link.replace("index.jsp?", 'userV2.do?method=login&')
    post_link += "&username={}&pwd={}".format(username, password)
    req = opener.open(post_link, urlencode(post_data))
    content = req.read()
    ip_reg = compile("http://(.+?)/")
    global ip_port
    ip_port = ip_reg.findall(auth_link)[0]
    return content


def iis_do_login(auth_link, username, password):
    post_data = auth_link.split("?")[-1]
    post_data += "&username={}&password={}".format(username, password)
    post_link = auth_link.replace("login.html", 'do.portallogin')
    try:
        req = opener.open(post_link, post_data, timeout=5)
        content = req.read()
        global ip_port
        ip_port = post_link
        return content
    except Exception as e:
        print(e)
        exit(1)


def iis_check_success(content):
    message = compile("<message>(.+?)</message>").findall(content)
    error_code = compile("<errcode>(.+?)</errcode>").findall(content)
    if error_code and int(error_code[0]) != 0:
        if 'linux' in platform or 'darwin' in platform:
            print("\033[01;31m{}\033[00m".format(message[0].strip()))
        else:
            print("{}".format(message[0].strip()))
        return False
    else:
        with open(tempfile.gettempdir() + "/IIS-WEB.logout", 'w') as handle:
            handle.write(ip_port.replace("do.portallogin", 'do.portallogoff'))

        ip = compile("wlanuserip=(.+?)&").findall(ip_port)
        if 'linux' in platform or 'darwin' in platform:
            print("IIS-WEB Login \033[01;31mSucceeded\033[00m!!")
            print("IP: \033[01;37m{}\033[00m".format(ip[0]))
        else:
            print("IIS-WEB Login Succeeded!!")
            print("IP: {}".format(ip[0]))
        return True


def check_success(content):
    uname = compile("d.userName.innerText='(.+?)'").findall(content)
    userip = compile("d.contentDive.userip='(.+?)'").findall(content)
    time_left = compile("d.maxLeaving.innerText='(.+?)'").findall(content)
    account_left = compile("d.accountInfo.innerText='(.+?)'").findall(content)
    logout_url = compile("d.toLogOut.href='(.+?)'").findall(content)
    if not uname or not userip:
        error_msg = compile("""<div id="errorInfo_center" val="(.+?)">""").findall(content)
        if error_msg:
            if 'linux' in platform or 'darwin' in platform:
                print("\033[01;31m{}\033[00m".format(error_msg[0].decode("gbk")))
            else:
                print("{}".format(error_msg[0]))
        else:
            print('Logging Failed......')
        return False
    else:
        temp_dir = tempfile.gettempdir()
        temp_file = temp_dir + "/{}-whu.logout".format(uname[0])
        with open(temp_file, 'w') as handle:
            handle.write('http://{}'.format(ip_port) + logout_url[0])

        if 'linux' in platform or 'darwin' in platform:
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

     -u     :username
     -p     :password
     -c     :config file

     -d  logout   :method for logout

     deploy like this:
        method 1. net-access-whu -u your_account -p your_password
        method 2. net-access-whu -c config.json

        config.json has the format like below(older edition, works always fine with only one type of network):
            {
                "username": "your_account",
                "password": "your_password"
            }
        or something like these
            {
                "COMMON": {
                    "username": "your_xiaoyuanwang_account",
                    "password": "your_xiaoyuanwang_password"
                },
                "IIS": {
                    "username": "your_guoraun_account",
                    "password": "your_guoruan_password"
                }
            }

        Logout(username is necessary for WHU network user, IIS user is not):

        method 1. net-access-whu -u your_account -d logout
        method 2. net-access-whu -c config.json -d logout
    """
    print(help_menu.__doc__)


def main():
    if not len(argv) == 3 and not len(argv) == 5:
        return help_menu()
    config = {
        'COMMON': {
            'username': '',
            'password': ''
        },
        'IIS': {
            'username': '',
            'password': ''
        }
    }
    username = ''
    password = ''
    for i in argv[1:]:
        if i == '-c':
            with open(argv[argv.index(i) + 1]) as handle:
                reader = handle.read()
            try:
                reader = json.loads(reader)
                config = reader
            except Exception as e:
                print(e)
                return help_menu()

            username = reader.get("username", '')
            password = reader.get("password", '')

            if not username and not password:
                common = reader.get("COMMON", '')
                iis = reader.get("IIS", '')
                if common:
                    username = common.get("username", '')
                    password = common.get("password", '')
                elif iis:
                    username = iis.get("username", '')
                    password = iis.get("password", '')
            break
        if i == '-u':
            username = argv[argv.index(i) + 1]
        if i == '-p':
            password = argv[argv.index(i) + 1]
    if 'logout' in argv[1:]:
        return logout(uname=username)

    auth_link, web_type = get_auth_link()

    if web_type == 'COMMON':
        check_success(do_login(auth_link, username, password))
    else:
        from_config = config.get("IIS", {})
        if from_config:
            username = from_config.get("username", '')
            password = from_config.get("password", '')
        iis_check_success(iis_do_login(auth_link, username, password))

if __name__ == '__main__':
    main()


