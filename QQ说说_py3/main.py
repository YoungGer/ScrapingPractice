# -*- coding:utf-8 -*-
import requests
import os,time
from bs4 import BeautifulSoup
from selenium import  webdriver

# 登陆
def logIn(name,pw):
    global driver
    driver.get('http://i.qq.com/')
    driver.maximize_window()
    driver.switch_to_frame(driver.find_element_by_id('login_frame'))
    upElement = driver.find_element_by_id('switcher_plogin')
    upElement.click()
    #输入账号密码，以及submit
    uElement = driver.find_element_by_id('u')
    pElement = driver.find_element_by_id('p') 
    uElement.clear()  
    uElement.send_keys(name)
    pElement.clear()
    pElement.send_keys(pw)
    time.sleep(1)
    loginB = driver.find_element_by_id('login_button')
    loginB.click()
    time.sleep(1)
    print ('登陆成功！')

def allPages():
    global driver
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    driver.find_element_by_id('_pager_content_0')
    bsPaperNum = BeautifulSoup(driver.page_source,'lxml')
    return int(bsPaperNum.find('a',title="下一页").previous_sibling.get_text())

def onePageInfo():
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    global driver
    bsObj = BeautifulSoup(driver.page_source,'lxml')
    times_contents = [[li0.find('a',class_='c_tx3').get_text(),li0.find('pre',class_='content').get_text()] \
    for li0 in bsObj.findAll('li',class_='feed')]
    return times_contents

def nextPage(i):
    global driver
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    driver.find_element_by_id('pager_next_'+str(i)).click()
    time.sleep(2)


if __name__ == '__main__':
    #初始化
    driver = webdriver.PhantomJS('/usr/local/phantomjs/bin/phantomjs')
    name = input('请输入登陆用的qq号')
    pw = input('请输入对应的qq密码')
    logIn(name,pw)
    driver.get(driver.current_url+'/311')
    time.sleep(1)
    driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    allPagesNum = allPages()
    TIMES_CONSTENTS = []
    for i in range(allPagesNum):
        print ('开始第',i+1,'页的收集')
        times_contents = onePageInfo()
        TIMES_CONSTENTS+=times_contents
        print ('结束第',i+1,'页的收集')
        try:
            nextPage(i)
        except:
            print ('全部完成！')

