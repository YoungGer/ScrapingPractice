# -*- coding:utf-8 -*-
import requests
import os,time,sys
from bs4 import BeautifulSoup
from selenium import  webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm

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
    if driver.current_url == "http://user.qzone.qq.com/"+name:
        print ('登陆成功！')
    else:
        print ('登陆失败，登录到'+driver.current_url)
        print ('请重新登陆 ')
        logIn(name,pw)


# 获得说说的页数
def allPages():
    global driver
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,'_pager_content_0'))
        )
    except:
        print ('allPages错误')
        return None
    else:
        driver.find_element_by_id('_pager_content_0')
        bsPaperNum = BeautifulSoup(driver.page_source,'lxml')
        return int(bsPaperNum.find('a',title="下一页").previous_sibling.get_text())

# 切换到下一页
def nextPage(i):
    global driver
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    try:
        element = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.ID,'pager_next_'+str(i)))
        )
    except:
        return None
    else:
        driver.find_element_by_id('pager_next_'+str(i)).click()
        return 1

# 获得这一页上面的说说信息
def onePageInfo():
    # 默认driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    global driver
    bsObj = BeautifulSoup(driver.page_source,'lxml')
    times_contents = [[li0.find('a',class_='c_tx3').get_text(),li0.find('pre',class_='content').get_text()] \
    for li0 in bsObj.findAll('li',class_='feed')]
    return times_contents

# 获得所有页面上的信息
def allPageInfo(query_name):
    global driver
    shuoshuo_index_url = "http://user.qzone.qq.com/"+query_name+'/311'
    driver.get(shuoshuo_index_url)
    #进入主要的iframe
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME,'app_canvas_frame'))
        )
    except TimeoutException:
        print ('初始化错误')
    else:
        driver.switch_to_frame(driver.find_element_by_class_name('app_canvas_frame'))
    allPagesNum = allPages()
    #开始提取信息
    TIMES_CONSTENTS = []
    for i in tqdm(range(allPagesNum)):
        # sys.stdout.write('\b\b开始第'+str(i+1)+'页的收集')
        # sys.stdout.flush()
        times_contents = onePageInfo()
        TIMES_CONSTENTS+=times_contents
        if i != allPagesNum-1:
            if nextPage(i)==None:
                print ('nextPage出错'+str(i))
                break
    print ('全部结束','共搜集了',allPagesNum,'页数据；共有',len(TIMES_CONSTENTS),'篇说说。')
    return TIMES_CONSTENTS



# 将信息保存到本地
def write2csv(TIMES_CONSTENTS,dest='test.csv'):
    p = pd.DataFrame(TIMES_CONSTENTS)
    p.to_csv(dest,index=False,header=['time','content'])
    print ('csv文件被写到：',os.getcwd()+'/'+dest)



if __name__ == '__main__':
    #初始化
    driver = webdriver.PhantomJS('/usr/local/phantomjs/bin/phantomjs')
    driver.implicitly_wait(1)
    name = input('请输入登陆用的qq号：')
    pw = input('请输入对应的qq密码：')
    logIn(name,pw)
    query_name = input('请输入查询说说的qq账号：')
    TIMES_CONSTENTS = allPageInfo(query_name)
    write2csv(TIMES_CONSTENTS,dest='bai.csv')




