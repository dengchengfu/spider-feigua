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

class FEIGUA():
    def get_html(self,url):
        headers = {
        "Accept": """*/*""",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6",
        "Connection": "keep-alive",
        "Cookie":  cookie,
        "Host": "dy.feigua.cn",
        "Referer": "https://dy.feigua.cn/Member",
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest" 
        }

        r=requests.get(url,headers=headers)
        html = r.text
        return html

    def get_args(self,keyword):
        base_url = "https://dy.feigua.cn/BloggerSearch/Search?"
        search_args = {
        "keyword": keyword,
        "isWithCommerceEntry": -1,
        "isWithLive": -1,
        "isBrandBlogger": -1,
        "hasContact": -1,
        "hasMcn": -1,
        "hasAdCreative": -1,
        "isUserBloggerClaim": -1,
        "showmodel": 0,
        "sort": 0,
        "page": 1
        }

        search_url = base_url + urlencode(search_args)
        
        html = self.get_html(search_url)
        soup = BeautifulSoup(html)
        ref = soup.select("body > div.v-search-items > div:nth-child(1) > div.search-item-btns > a:nth-child(1)")[0]['href']
        signature = ref.split('&signature=')[1]
        timestamp = ref.split('&signature=')[0].split('&timestamp=')[1]
        _id = ref.split('&timestamp=')[0].split('?id=')[1]
        print("个人主页参数",(_id,timestamp,signature))

        return (_id,timestamp,signature)


    def get_uid_fan(self,_id,timestamp,signature):
        def get_fanTotal(html):
            soup = BeautifulSoup(html)
            fan = soup.select("body > div.v-main > div > div.v3-owner.owner-info-bozhu > div > div.flex-column-col2.scrollbar > div > ul:nth-child(2) > li:nth-child(1) > strong")[0].text
            fan = float(fan[:-1])
            return fan

        def get_uid(html):
            #方法一
            soup = BeautifulSoup(html)
            uid = soup.select("#uid")[0]['value']

            #方法二
            #re.compile()函数接受一个标志参数叫re.DOTALL,它可以让正则表达式中的点（.）匹配包括换行符在内的任意字符。
            #js = re.compile('(.*)param(.*)pagesize',re.DOTALL)
            #js.search(html).group(2)
            return uid
        
        def get_nickname(html):
            #方法一
            soup = BeautifulSoup(html)
            nickname = soup.select("body > div.v-main > div > div.v3-owner.owner-info-bozhu > div > div.v3-owner-info > div.media-list.v3-owner-bozhu > div.item-inner > div.item-title > a.title")[0].text
            # print(nickname)
            return nickname

        #个人主页链接
        url = "https://dy.feigua.cn/BloggerNew/Detail?id={}&active=bloggerdata&timestamp={}&signature={}".format(_id,timestamp,signature)
        print("个人主页链接",url)
        html = self.get_html(url)
        
        fan = get_fanTotal(html)
        uid = get_uid(html)
        nickname = get_nickname(html)
        
        print("个人主页详情",(nickname,uid,fan))
       
        return (nickname,uid,fan)


    def get_portrait(self,_id,uid,nick):
        def get_portrait_html(url):
            headers = {
            "Accept": """*/*""",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6",
            "Connection": "keep-alive",
            "Cookie":  cookie,
            "Host": "dy.feigua.cn",
            "Referer": "https://dy.feigua.cn/Member",
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest" 
            }

            r=requests.get(url,headers=headers)
            html = r.text
            return html

        def get_gender(html,gen_type):
            soup = BeautifulSoup(html)
            if "synthesis" in gen_type:
                name = fantab_dict[gen_type]
                selector = "#synthesis_container > div.container-fluid > div > div:nth-child(1) > div > div:nth-child(2) > div > div.gender-percentage"  
            if "aweme" in gen_type:
                name = fantab_dict[gen_type]
                selector = "#aweme_container > div.container-fluid > div > div:nth-child(1) > div > div:nth-child(2) > div > div.gender-percentage"
            
            gen_data = []
            if soup.select(selector) != []:
                data = soup.select(selector)[0].text.split("\n")
                for i in range(1,3):
                    #中文的冒号
                    gender = data[i].split('：')[0]
                    pct = float(data[i].split('：')[1][:-1])
                    gen_data.append((nick,name,gender,pct))
            return gen_data
    
        def get_age(html,fan_type):
            if "synthesis" in fan_type:
                name = fantab_dict[fan_type]
                age_str = re.search('(.*)synthesis_age_chart\",(.*)[)]',html).group(2)
            if "aweme" in fan_type:
                name = fantab_dict[fan_type]
                age_str = re.search('(.*)aweme_age_chart\",(.*)[)]',html).group(2)
                
            age_set = []
            if age_str != "null":
                total = 0
                age_data = eval(age_str)
                for data in age_data:
                    total = total + data['Samples']
                
                for data in age_data:
                    age_set.append((nick,name,data['Name'],data['Samples']/total))

            return age_set 
        
        #粉丝页面链接
        url = 'https://dy.feigua.cn/BloggerNew/Loadbloggerfans?id={}&uid={}&showDemo=false&_={}'.format(_id,uid,round(time.time() * 1000))
        print("粉丝页面链接",url)
        html = get_portrait_html(url)
        
        fan_gender_data = get_gender(html,"synthesis")
        video_gender_data = get_gender(html,"aweme")
        
        fan_age_data = get_age(html,"synthesis")
        video_age_data = get_age(html,"aweme")
        
        print("粉丝画像:")
        print((fan_gender_data,video_gender_data,fan_age_data,video_age_data))
        return (fan_gender_data,video_gender_data,fan_age_data,video_age_data)
