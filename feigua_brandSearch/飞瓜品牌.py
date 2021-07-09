#导入库
import random
import time
import os
import re
import requests
import webbrowser
import pandas as pd 
import time
import json
from bs4 import BeautifulSoup
from lxml import etree
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from settings import *

def get_html(url):
        headers = {
        "Accept": """*/*""",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie":  COOKIE,
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
        html = r.content
        return html

#return urls (product_name,product_atv,product_url)
def get_itemList(total_num)
	base_url = "https://dy.feigua.cn/PromotionBrandNew/LoadPromotionAnalysis?page={}&brandId=98&ispartial=true&fromDate=2021-04-10&toDate=2021-07-08&sort=6&cateid=0&cate1id=&cate2id=&days=&keyword=%E5%8D%B8%E5%A6%86%E8%86%8F&_=1625824566395"
	item_links = []
	endPage = total_num//10
	for i in range(1,endPage+2):
		item_links.append(base_url.format(i))

	urls = []
	count = 1
	for link in item_links:
	    html = get_html(link)
	    soup = BeautifulSoup(html)
	    refs = soup.select("div.item-inner > div.item-title > a")
	    prices = soup.select("div.item-price > span.price")
	    titles = soup.select("div.item-inner > div.item-title > a")
	    
	    for title,price,ref in zip(titles,prices,refs):
	        name = title.get_text().replace('\n',"").replace('\r',"").strip()
	        atv = price.get_text().split('￥')[1].split('\r')[0]
	        url = 'https://dy.feigua.cn/Member' + ref['href']
	        urls.append((name,atv,url))
	        print(count,(name,atv,url))
	        count += 1
	    time.sleep(random.uniform(0.5,2))

	return urls


#return liveCount_gids (liveCount,gid,product_name,product_atv)
def get_liveCount(urls):
	liveCount_gids = []
	base_url = "https://dy.feigua.cn/GoodsNew/LoadLiveAnalysisChartData?"
	count = 1
	for url in urls:
	    parser = urlparse(url[2])
	    query = parser.fragment
	    query_dict = parse_qs(query)
	    
	    #获取Gid, promotionid 与 Gid 有时候会不一致, Gid才能返回正确的数值
	    profile_url = "https://dy.feigua.cn/GoodsNew/Detail?" + url[2].split('?')[1]
	    html = get_html(profile_url)
	    soup = BeautifulSoup(html)
	    gid = soup.select('#gid')[0]['value']
	    time_stamp = round(time.time() * 1000)
	    
	    search_args = {
	        "FromDate": "2021-01-10",
	        "ToDate": "2021-07-08",
	        "Gid": gid,
	        "IsLiveing": 0,
	        "_": time_stamp
	    }
	    zb_url = base_url + urlencode(search_args)
	    
	    html = get_html(zb_url)
	    html_str = str(html,'utf-8')
	    html_json = json.loads(html_str)
	    
	    liveCount_gids.append((html_json['liveCount'],gid,url[0],url[1]))
	    print(count,gid,'liveCount:',html_json['liveCount'])
	    count += 1
	    time.sleep(random.uniform(0.5,1))

	return liveCount_gids


#return zb_links (product_name,product_atv,zb_url)
def get_zblinks(liveCount_gids):
	detail_base = "https://dy.feigua.cn/GoodsNew/LoadLiveAnalysisData?"
	count = 1

	zb_links = []
	for i in liveCount_gids:
	    print(count,"一共有{}场直播".format(i[0]))
	    if i[0] != '--':
	        print("近期有直播",i)
	        total_items = int(i[0])
	        endPage = total_items//10
	        num = 1
	        for j in range(1,endPage+2):
	            detail_args = {
	            "Sort": "2",
	            "FromDateCode": "2021-01-09",
	            "ToDateCode": "2021-07-07",
	            "Page": j,
	            "Gid": i[1],
	            "IsLiveing": 0,
	            "_" : round(time.time() * 1000)
	            }

	            zb_url = detail_base + urlencode(detail_args)
	            print("{}-{}".format(count,num),zb_url)
	            zb_links.append((i[2],i[3],zb_url))
	            num += 1
	    count +=1

	return zb_links


if __name__ == '__main__':

	total_num = input('输入品牌商品总数: ')
	urls = get_itemList(int(total_num))
	liveCount_gids = get_liveCount(urls)
	zb_links = get_zblinks(liveCount_gids)

	datas = []
	count = 1
	total = len(zb_links)

	start = time.time()
	for zb in zb_links:
	    detail_url = zb[2]
	    html = get_html(detail_url)
	    soup = BeautifulSoup(html)

	    #爬取直播名
	    live_soups = soup.select("div.media-list.v3-media-live")

	    live_names = []
	    for soup in live_soups:
	        livename = soup.get_text().replace('\n',"")
	        live_names.append(livename)

	    #爬取博主名
	    bozhu_soups = soup.select("div.media-list.v3-media-bozhu.v3-media-bozhu-m")

	    bozhu_names = []
	    for soup in bozhu_soups:
	        bozhuname = soup.get_text().replace('\n',"")
	        bozhu_names.append(bozhuname)
	        
	    #爬取直播时间
	    date_soups = soup.select('td.text-center')
	    
	    starts = []
	    ends = []
	    for d in range(0,len(date_soups),5):
	        zb_time = date_soups[d].get_text()
	        mid = len(zb_time)//2
	        start = zb_time[0:mid]
	        end = zb_time[mid:]
	        starts.append(start)
	        ends.append(end)

	    #爬取直播销量
	    sale_soups = soup.select("div.v3-arrow-tip")
	 
	    amounts = []
	    for j in range(0, len(sale_soups),2):
	        #print(sale_soups[j].get_text())
	        num = sale_soups[j].get_text().split('\n')[1].strip()
	        amounts.append(num)
	    
	    #数据存储
	    for live_name,bozhu_name,start,end,amount in zip(live_names,bozhu_names,starts,ends,amounts):
	        print("{}/{}".format(count,total),zb[0],zb[1],live_name,bozhu_name,start,end,amount)
	        datas.append((zb[0],zb[1],live_name,bozhu_name,start,end,amount))
	    
	    #休息
	    time.sleep(random.uniform(0.5,1))
	    count +=1

	    #统计运行时间
	    end = time.time()
		duration_s = round(end-start,1)
	    duration_min = round(duration_s/60,2)
	    print("截止当前耗时: {}s,".format(duration_s), "{}min".format(duration_min))
	    print('-'*50)


	#统计运行时间
	end = time.time()
	duration_s = round(end-start,1)
    duration_min = round(duration_s/60,2)
    print("总耗时: {}s,".format(duration_s), "{}min".format(duration_min))
    

	#导出文件
	header = ["商品名称","件单价","直播","博主","开始时间","结束时间","销量"]
	fil_title = "飞瓜"
	filname = fil_title + "过往180天直播情况" + ".csv"
	details=pd.DataFrame(columns=header,data=datas)
	print(details.info())
	#解决中文乱码
	details.to_csv(filname,encoding = "utf_8_sig")
	print('已成功导出!')

