# -*- coding: utf-8 -*-
'''
输入需要查看的人
输出查看人的被关注的人群
'''


from bs4 import BeautifulSoup
import requests
import re
from functools import reduce
import pandas as pd
import json
import os
from tqdm import tqdm


def signIn():
    '''
    登陆
    '''
    # email = input('请输入知乎的用户名:')
    # password = input('请输入知乎的密码:')
    email = 'tjuygy@163.com'
    password = 'a433991100'
    # 登陆
    loginUrl = "https://www.zhihu.com/login/email"
    login_data = {'email': email, 'password': password}
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
        'Host': 'www.zhihu.com',
        'Referer': 'http://www.zhihu.com/'
    }
    session = requests.session()
    r = session.post('http://www.zhihu.com/login/email', data=login_data, headers=header)
    # 判断登陆是否成功
    if r.json()['r']==0:
        print ("您已成功登陆知乎")
        return session
    else:
        print ("登陆失败")
        return None


def stringToUserInfo(s):
    '''
    输入s：html字符串
    输出titles_hrefs_imgs:对应该字符串的用户信息
    '''
    bsObj = BeautifulSoup(s)
    titles_hrefs_imgs = [[tag.a['title'] ,tag.a['href']] for tag in bsObj.findAll("h2", class_="zm-list-content-title") ]
    imgs  = [tag['src'] for tag in bsObj.findAll('img',class_='zm-item-img-avatar')]
    [t.append(imgs[i]) for i,t in enumerate(titles_hrefs_imgs)]
    return titles_hrefs_imgs

def userInfo(session,name):
    url = 'https://www.zhihu.com/people/'+name+'/followers'
    header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/people/'+name+'/followers'
    }
    req = session.get(url,headers=header)
    bsObj = BeautifulSoup(req.content.decode('utf-8'))
    # 找到基本的信息
    s = req.content.decode('utf-8')
    hash_id = re.findall('hash_id&quot.*?;([\w]+)&quot;',s)[0]
    _xsrf = bsObj.find('input',{"name":"_xsrf"})['value']
    # 找到关注了和关注者
    guanZhuNum = int(bsObj.find(lambda tag:tag.get_text()=='关注了').next_sibling.next_sibling.next_sibling.get_text())
    guanZhuEdNum = int(bsObj.find(lambda tag:tag.get_text()=='关注者').next_sibling.next_sibling.next_sibling.get_text())
    print (name+'关注了'+str(guanZhuNum)+'人，'+'被'+str(guanZhuEdNum)+'人关注。\n')
    # 循环more找到所有被关注的人
    S = reduce(lambda x,y:x+y,[str(tag) for tag in bsObj.findAll('div',class_='zm-profile-card')])


    for i in tqdm(range(guanZhuEdNum//20)):
        offset = (i+1)*20
        params = json.dumps({"offset":offset, "order_by": "created", "hash_id": hash_id})
        data = {
                                '_xsrf': _xsrf,
                                'method': "next",
                                'params': params
        }
        res_post = session.post('https://www.zhihu.com/node/ProfileFollowersListV2',data=data,headers=header)
        S = S + reduce(lambda x,y:x+y,(res_post.json()['msg']))
    # 找完后，统一用BS提取信息
    titles_hrefs_imgs = stringToUserInfo(S)
    return titles_hrefs_imgs

def write2csv(titles_hrefs_imgs,dest):
    p = pd.DataFrame(titles_hrefs_imgs)
    p.to_csv(dest,index=False,header=['name','url','image'])
    print ('csv文件被写到：',os.getcwd()+'/'+dest)

def write2mysql(titles_hrefs_imgs,dest='zhihu',name='root',pw='root',db='scraping'):
    import pymysql
    from sqlalchemy import  create_engine
    p = pd.DataFrame(titles_hrefs_imgs)
    engine = create_engine('mysql+pymysql://'+name+':'+pw+'@localhost:3306/'+db+'?charset=utf8')
    p.to_sql(dest,engine)
    


if __name__ == '__main__':
    # 首先进行登陆的测试
    session = signIn()
    if session==None:
        raise ValueError('登陆失败')
    # 统计该账户下的基本信息
    titles_hrefs_imgs = userInfo(session,name='caijia')
    # 写入信息
    write2csv(titles_hrefs_imgs,dest='caijia.csv')
    # write2mysql(titles_hrefs_imgs,dest='132',name='root',pw='root',db='scraping')



