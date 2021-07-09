#导入库
import random
import time
import os
import re
import requests
from lxml import etree
import pandas as pd 
import time
import re
import json
from bs4 import BeautifulSoup
from lxml import etree
from urllib.parse import urlencode
import feigua

def data_process(data):
    data_Tuple = ()
    for i in data:
        data_Tuple = data_Tuple + i
    data_List = []
    for i in data_Tuple:
        data_List = data_List + i
    return data_List


cookie = """"""
#读取文件
df = pd.read_excel("CK补充达人.xlsx")
#用户列表
nicknames = df['达人名称'].tolist()
#选择行数
nicknames = nicknames[:]
fantab_dict = {
    "synthesis":"粉丝列表画像",
    "aweme":"视频观众画像"
}


### --------------------爬取入口---------------------
#实例化类
feigua =  FEIGUA()

overview = []
fan_gender = []
fan_portrait = []
count = 0
error = []
print("一共需爬取{}个达人".format(len(nicknames)))
print("*"*50)

for nick in nicknames:
    try:
        count += 1
        print("开始爬取第{}个达人: ".format(count),nick)
        _id, timestamp, signature = feigua.get_args(nick)
        time.sleep(random.uniform(0.3,1))
        nick_name,uid, fan = feigua.get_uid_fan(_id,timestamp,signature)
        time.sleep(random.uniform(0.3,1))
        overview.append((nick,nick_name, fan, _id, uid))
        data = feigua.get_portrait(_id,uid,nick_name)
        fan_gender.append((data[0],data[1]))
        fan_portrait.append((data[2],data[3]))
        print("第{}个达人爬取完毕".format(count))
        print("*"*50)
    except Exception as e:
        print("达人{}不存在".format(nick),e)
        error.append(nick)
        print("*"*50)


### 个人主页数据处理
overview_header = ["原始昵称", "昵称","粉丝数(万)","id","uid"]
filname = "CK补充达人飞瓜抖音粉丝TOP" + str(len(overview)) + ".csv"
details=pd.DataFrame(columns=overview_header,data=overview)
print(details.info())
#解决中文乱码
details.to_csv(filname,encoding = "utf_8_sig")


### 处理粉丝性别画像
gender_header = ["昵称","画像属性","性别","占比"]
fanList = data_process(fan_gender)
filname = "CK补充达人飞瓜抖音粉丝性别画像TOP" + str(len(overview)) + ".csv"
details=pd.DataFrame(columns=gender_header,data=fanList)
print(details.info())
#解决中文乱码
details.to_csv(filname,encoding = "utf_8_sig")


### 处理粉丝年龄画像
age_header = ["昵称","画像属性","年龄","占比"]
portraitList = data_process(fan_portrait)
filname = "CK补充达人飞瓜抖音粉丝年龄画像TOP" + str(len(overview)) + ".csv"
details=pd.DataFrame(columns=age_header,data=portraitList)
print(details.info())
#解决中文乱码
details.to_csv(filname,encoding = "utf_8_sig")
