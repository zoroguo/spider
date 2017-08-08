# -*- coding: utf-8 -*-
'''
Created on Thu Jun  16 22:16:00 2017

@author: guozhijun

说明： 1.抓取猎聘网招聘内容
      2.内容：

      数据暂时存放在mysql的temp.spider_tieba_egui中
create table spider_liepin
(
    id int(5) NOT NULL auto_increment COMMENT '主键',
    create_time datetime COMMENT '创建记录时间',
    title varchar(100) COMMENT '职位',
    summary varchar(100) COMMENT '简介',
    salary varchar(100) COMMENT '薪资范围',
    city  varchar(100) COMMENT '城市',
    publish_time varchar(100) COMMENT '发布时间',
    graduate varchar(30) COMMENT '学历',
    workyears varchar(50) COMMENT '工作年限',
    language varchar(50) COMMENT '外语',
    age varchar(50) COMMENT '年龄',
    position_desc text COMMENT '岗位描述',
    other_info text COMMENT '其它信息',
    salary_welfare varchar(1000) COMMENT '薪酬福利',
    company_intruduce text COMMENT '公司介绍',
    detail_url varchar(200) COMMENT '详细页面url',
    pageid varchar(10) COMMENT '所在页数',
    PRIMARY KEY  (id)
)engine=innodb;

'''

import urllib.request
import urllib.parse
from urllib import error
from bs4 import BeautifulSoup
import re,datetime,pymysql
from pymongo import MongoClient
from log import Logger

'''
数据批量插入mysql库中
charset='utf-8'
会报错AttributeError: 'NoneType' object has no attribute 'encoding'
mysql库中竟然不识别utf-8
'''
datetm=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def operate_mysql(position):
    conn = pymysql.connect(host='localhost',
                           port= 3306,
                           user = 'root',
                           passwd='root',
                           db='temp',
                           use_unicode=True,
                           charset='utf8')
    #创建游标
    cur = conn.cursor()
    sql="insert into spider_liepin(create_time,title,summary,salary,city,publish_time,graduate," \
                    "workyears,language,age,position_desc,other_info,salary_welfare," \
                    "company_intruduce,detail_url,pageid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    cur.executemany(sql,tuple(position))
    '''
    cur.executemany("insert into spider_liepin(create_time) values(%s)", \
                    [(datetm)])
    '''
    #提交
    conn.commit()
    #关闭指针对象
    cur.close()
    #关闭连接对象
    conn.close()

#目标网页 数据挖掘&北京 获取信息：招聘职位、公司、薪资、地点、发布时间、要求标签（本科、3年以上、语言、年龄）、职位描述
#其他信息、薪酬福利、企业介绍
para=urllib.parse.quote('数据挖掘'.encode('utf-8'))
search_url='https://www.liepin.com/bj/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&key='
start_url=search_url+para
print(start_url)

#headers头信息
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
         'Referer': 'https://www.liepin.com/bj/zhaopin/'}

def getResponse(url):
    request = urllib.request.Request(url,headers=headers)
    response = urllib.request.urlopen(request)
    if 'error' in response.url.lower():
        print('The page does not exist and has been redirected!')
        return None
    else:
        bsobj=BeautifulSoup(response,'lxml')
        return bsobj

def getPages(bsobj):
    pattern=re.compile('curPage=(\d+)" title="末页"',re.S)
    page_info=str(bsobj.find_all(class_="pagerbar"))
    #print (page_info)
    pages=re.findall(pattern,page_info)
    return pages

def parse(bsobj):
    #获取页面的href
    position = []
    zhaopin_info=bsobj.find_all(class_='job-info')
    for info in zhaopin_info:
        for href in info.find_all('a'):
            href=href.get('href')
            print(href)
            log.info(href)
            detail=getResponse(href)
            #职位
            title=detail.h1.get_text()
            summary=detail.h3.get_text()
            #薪资
            salary=detail.find_all(class_="job-item-title")[0].get_text().strip()
            #城市、发布时间、学历要求、工作年限要求、语言要求、年龄要求
            baseInfo=detail.find_all(class_="basic-infor")[0].find_all('span')
            city=baseInfo[0].get_text()
            publish_time=baseInfo[1].get_text()
            baseInfo2=detail.find_all(class_="job-qualifications")[0].find_all('span')
            graduate=baseInfo2[0].get_text()
            workyears=baseInfo2[1].get_text()
            language=baseInfo2[2].get_text()
            age=baseInfo2[3].get_text()
            #岗位描述
            position_desc=detail.find_all(class_="job-item main-message")[0].get_text()
            other_info=detail.find_all(class_="job-item main-message")[1].get_text()
            #薪酬福利
            salary_welfare=detail.find_all(class_="tag-list")[0].get_text()
            #公司介绍
            company_intruduce=detail.find_all(class_="job-item main-message noborder")[0].get_text()
            position.append([datetm,title.strip(),summary,salary,city,publish_time,graduate,workyears,language,age,position_desc,other_info,salary_welfare,company_intruduce,href,pageid])
            log.info(position)
            #print(position)
            #数据插入数据库中
    operate_mysql(position)
    #print(position)

if __name__=='__main__':
    global log
    log=Logger()
    page_obj=getResponse(start_url)
    end_page=int(getPages(page_obj)[0])+1

    for pageid in range(end_page):
        detail_url=start_url+'&curPage='+str(pageid)
        log.info(detail_url)
        detail_obj=getResponse(detail_url)
        #参考spider_qiubai.py 将数据写入mysql进行分析
        try:
            parse(detail_obj)
        except IndexError as e:
            log.error(e)