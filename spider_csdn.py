# -*- coding: utf-8 -*-
"""
Created on Wed May 31 13:49:59 2017

@author: guozhijun
"""


import urllib.request
from urllib.parse import urlencode
import http.cookiejar
#import re
from bs4 import BeautifulSoup
from urllib import error

#登录地址
url = "https://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn"

#创建一个cookie对象
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
response = opener.open(url)
bsobj=BeautifulSoup(response,'lxml')
print(bsobj.find_all('input'))
#读取lt及execution的值 因这两个值为登录随机值
lt=bsobj.find_all('input')[3]["value"]
execution=bsobj.find_all('input')[4]["value"]

#post信息
values = {"username":"账号",
          "password":"密码",
          "lt":lt,
          "execution":execution,
          "_eventId":"submit",
          }

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
         'Referer': 'http://www.csdn.net/',}

#urlencode()函数原理就是首先把中文字符转换为十六进制，然后在每个字符前面加一个标识符%          
data = urlencode(values).encode(encoding='utf-8') 

print(data)

#构造request对象请求
request = urllib.request.Request(url,data,headers=headers)
#添加error异常处理部分
try:
    response = opener.open(request)#urllib.request.urlopen(request)
    #打印登录后的页面 
    print (response.read().decode('utf-8'))
except error.HTTPError as e:
    print(e.code)
    print(e.reason)
except error.URLError as e:
    print(e.code)
    print(e.reason)    

'''
打印出的页面含有用户名，用户ID等登录后的信息。
模拟登录成功
'''
