# -*- coding: utf-8 -*-
'''
Created on Thu Jun  4 16:58:00 2017

@author: guozhijun

说明： 1.抓取百度贴吧-英雄志吧关注人
      2.内容：饿鬼昵称、性别、吧龄、发帖量、爱逛的吧(关注贴吧名及等级)、关注的人数、粉丝人数、T豆数、蓝钻数、礼物数

      数据暂时存放在mysql的temp.spider_tieba_egui中
create table spider_tieba_egui
(
    id int(5) NOT NULL auto_increment COMMENT '主键',
    create_time datetime COMMENT '发布时间',
    peo_name varchar(100) COMMENT '昵称',
    gender varchar(100) COMMENT '性别',
    age int COMMENT '吧龄',
    post_cnt int COMMENT '发帖量',
    focus_cnt int COMMENT '关注的人数',
    fan_cnt int COMMENT '粉丝人数',
    t_dou int COMMENT 'T豆数',
    bule_diamond_cnt int COMMENT '蓝钻数',
    gift_cnt int COMMENT '详细页面url',
    PRIMARY KEY  (id)
)engine=innodb;

     3. 流程：a) 模拟登录 佛本红尘一浪子/******
             b) 以 http://tieba.baidu.com/bawu2/platform/listMemberInfo?word=%E8%8B%B1%E9%9B%84%E5%BF%97&ie=utf-8&red_tag=u0594837291
                 为起点，遍历抓取用户信息
             c) 获取所有关注人详细信息url
             d) 遍历所有详细信息url，从中取出相关字段信息
             e) 批量插入mysql库中

鉴于用户关注贴吧数未知，数据首先处理到mongdb中

可配置化。word=parameter（此处参数为贴吧名，获取关注贴吧用户）
http://tieba.baidu.com/bawu2/platform/listMemberInfo?word=英雄志BE&pn=1
'''

import urllib.request
import urllib.parse
from urllib import error
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from log import Logger

#连接mongdb数据库
def mongodb(tabna,collections):
    client = MongoClient('localhost', 27017)
    #db_auth = client.admin
    #db_auth.authenticate("account", "password")
    #admin 数据库有帐号，连接-认证-切换库
    db = client.test
    #数据插入mongo库中
    db.tabna.insert_many(p for p in collections)

#headers头信息
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
         'Referer': 'http://tieba.baidu.com/',}

#服务器端页面信息
def getResponse(url):
    request = urllib.request.Request(url,headers=headers,)
    response = urllib.request.urlopen(request)
    if 'error' in response.url.lower():
        print('The page does not exist and has been redirected!')
        return None
    else:
        bsobj=BeautifulSoup(response,'lxml')
        return bsobj

#获取所有关注用户url

#获取fans总页数
def getPages(response):
    pattern=re.compile('\d+',re.S)
    pages=re.findall(pattern,str(response.find_all(class_="tbui_total_page")))
    return pages

#解析详情页面，返回各关键信息
def parse(url,pn=1,pages=2):
    for pn in range(pn,pages):
        collections=[]
        url=url+'&pn='+str(pn)
        print(url)
        onepage=getResponse(url)
        fans=onepage.find_all(class_='user_name')
        for fan in fans:
            hostpage='http://tieba.baidu.com'+fan.get('href')
            log.info(hostpage)
            detail=getResponse(hostpage)
            #昵称
            peo_name=fan.get('title')
            #吧龄、发帖量、会员天数
            gender='other'
            baling=0
            post=0
            concerns=0
            fens=0
            if detail is not None:
                userdata=detail.find_all(class_="userinfo_userdata")
                #print(userdata)
                pattern=re.compile('userinfo_sex userinfo_sex_(.*)"></span><span>'\
                               '吧龄:(.*)</span><span class="userinfo_split">.*发贴:(\d+)</span>',re.S)
                user_data=re.findall(pattern,str(userdata))
                log.info(user_data)
                if len(user_data)>0:
                    gender=user_data[0][0]
                    print(gender)
                    baling=user_data[0][1]
                    post=user_data[0][2]
                #关注数、个人fans数
                concern_num=detail.find_all(class_="concern_num")
                pattern=re.compile('>(\d+)')
                items=re.findall(pattern,str(concern_num))
                if len(items)>1:
                    concerns=items[0]
                    fens=items[1]
            '''
            #关注贴吧 该点比较难抓取。用户若隐藏动态，则返回空，否则抓取用户所关注所有贴吧及所在贴吧等级。
            concern_tieba=detail.find_all(class_="u-f-item unsign")
            if concern_tieba:
                pattern=re.compile('<span>(.*)</span><span class="forum_level (.*)"></span>',re.S)
                tieba=detail.find_all(class_="u-f-item unsign")
                re.findall(pattern,str(tieba[0]))
            '''
            print(gender)
            #每一页抓取的数据放到同一个列表中，每页批量插入mongdb中
            fanInfo={'peo_name':peo_name,
                     'gender':gender,
                     'baling':baling,
                     'post':post,
                     'concerns':concerns,
                     'fans':fens,
                     'concern_tieba':'英雄志',
                     'hosturl':hostpage
                     }
            print(fanInfo)
            collections.append(fanInfo)
        #print(collections)
        if len(collections)>0:
            mongodb('spider_tieba',collections)
        log.info('已完成%s页',pn)          

#调试代码。当直接执行该文件时，则执行__name__=='__main__'。
#当从别的模块导入时则不执行
if __name__=='__main__':
    global log
    log=Logger()
    #url中不能含中文，先编码成gbk字符集。然后由quote处理
    #quote 屏蔽特殊的字符或者转换特殊字符为url允许标准（含中文）
    para=urllib.parse.quote('英雄志'.encode('gbk'))
    startUrl='http://tieba.baidu.com/bawu2/platform/listMemberInfo?word='+para
    firstRes=getResponse(startUrl)
    pages=int(getPages(firstRes)[0])
    print(pages)
    try:
        parse(startUrl,1620,pages+1)
    except IndexError as e:
        log.error(e)
    except error.HTTPError as e:
        log.error(e)
    except error as e:
        log.error(e)
        