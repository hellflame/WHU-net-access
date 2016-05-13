# coding=utf8
from setuptools import setup, find_packages

docs = """武大校园网终端认证
#####################

个人用登录武大校园网终端小工具(已经懒的开浏览器了....)

安装
=====

.. code:: bash

  $ sudo pip install net-access-whu


使用
====
* 直接登录

.. code:: bash

  $ net-access-whu -u 2020301260064 -p hellflame


* 配置文件登录

.. code:: bash

  $ net-access-whu -c login.json

`login.json` 文件格式
.. code::

  {
    "username": 2020301260064,
    "password": "hellflame"
  }

之后就等着查看返回消息就好了

"""
setup(
    name='net-access-whu',
    version='0.0.2',
    keywords=('network auth', 'WHU'),
    license='Apache License',
    description="终端登录武汉大学校园网",
    author="hellflame",
    author_email="hellflamedly@gmail.com",
    url="https://github.com/hellflame/WHU-net-access",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent"
    ],
    platforms='all',
    entry_points={
        'console_scripts': [
            'net-access-whu=net_access:main'
        ]
    }
)






