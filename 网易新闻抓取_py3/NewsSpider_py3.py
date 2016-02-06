# -*- coding:utf-8 -*-
import requests
import os
from bs4 import BeautifulSoup
import csv



#首先获取各个项目的子目录
def getAllSubsets(url= "http://news.163.com/rank/",):
	"""
	输入对应新闻的url；
	输出一个数组，每个元素是(title,href)的元组，
	title指子新闻的名字
	href指子新闻的链接
	"""
	res = requests.get(url)
	bsObj = BeautifulSoup(res.content.decode('gbk'),fromEncoding='gbk')
	urls_tag = bsObj.findAll(lambda tag:tag.get_text()=='更多'and tag.name=='a') #找到对应的关键tag
	titles = [url_tag.parent.previousSibling.get_text() for url_tag in urls_tag]
	hrefs = [url_tag['href'] for url_tag in urls_tag]
	titles_hrefs = zip(titles,hrefs)
	return titles_hrefs

#统计各个子目录下面的本周点击排行
def getSubsetContent(title,url):
	res = requests.get(url)
	bsObj = BeautifulSoup(res.content.decode('gbk')) 
	assert bsObj.find(class_='titleBar').h2.get_text()==title #确认找到正确的网站
	#找到tabContents,只统计本周点击排行
	x = bsObj.findAll(class_='tabContents')[2]
	hrefs = [tag.a['href'] for tag in x.findAll('td')  if tag.a != None]
	titles = [tag.a.get_text() for tag in x.findAll('td') if tag.a != None]
	assert len(hrefs)==len(titles)
	titles_hrefs = zip(titles,hrefs)
	return (titles_hrefs,title)

#写文件到csv中
def write2csv(titles_hrefs,title):
	if not os.path.exists('./网易新闻抓取_py3/'):
		os.makedirs('./网易新闻抓取_py3/')
	with open('./网易新闻抓取_py3/'+title+'.csv','w') as f:
		writer = csv.writer(f)
		writer.writerow(['title','url'])
		writer.writerows(titles_hrefs)

if __name__ == '__main__':
	for (title,url) in getAllSubsets():
		titles_hrefs,title = getSubsetContent(title,url)
		write2csv(titles_hrefs,title)