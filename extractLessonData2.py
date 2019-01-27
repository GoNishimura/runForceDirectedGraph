# -*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

year = 2018
urls = [
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_5.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_8.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_9.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_10.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_11.html".format(year)
]
allPages = [
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_2.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_3.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_4.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_5.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_6.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_7.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_8.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_9.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_10.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_11.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_12.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_13.html".format(year),
    "http://vu.sfc.keio.ac.jp/course_u/data/{}/csec14_15.html".format(year)
]

allId = set()
idToName = {}
idToPageId = {}

for idx, url in enumerate(allPages):
    with urllib.request.urlopen(url) as f:
        html = f.read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        courses = soup.find('ul', class_='clist').find_all('a')
        for course in courses: 
            allId.add(course.string[:5])
            idToName[course.string[:5]] = course.string[6:]
            idToPageId[course.string[:5]] = idx

dfNode = pd.DataFrame({'id':list(idToName.keys())})
for row in range(dfNode.shape[0]):
    dfNode.at[row, 'name'] = idToName[dfNode.at[row, 'id']]
    dfNode.at[row, 'group'] = idToPageId[dfNode.at[row, 'id']]
dfNode = dfNode.astype({'group':int})

dfLink = pd.DataFrame(columns=['source', 'target', 'left', 'right'])

for url in allPages:
    with  urllib.request.urlopen(url) as f:
        html = f.read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        courses = soup.find_all('div', class_='course')
        
        for idx, course in enumerate(courses):
            kanren = course.table.find(string='関連科目')
            zentei = course.table.find(string='前提科目（推奨）') # returns None if not found
            hissu = course.table.find(string='前提科目（必須）')
            courseId = course.find('div', class_='course_title').get_text()[:5]
            if courseId in allId:
                courseNode = dfNode[dfNode['id'].isin([courseId])]
                if kanren != None:
                    for content in kanren.find_parent('tr').select('td:nth-of-type(2)')[0]:
                        if content.name == 'a' and content.string[1:6] in allId: 
                            contentNode = dfNode[dfNode['id'].isin([content.string[1:6]])]
                            dfLink = dfLink.append(pd.DataFrame({'source':contentNode.iat[0,0], 'target':courseNode.iat[0,0], 'left':['false'], 'right':['false']}), ignore_index=True)
                if zentei != None:
                    for content in zentei.find_parent('tr').select('td:nth-of-type(2)')[0]:
                        if content.name == 'a' and content.string[1:6] in allId: 
                            contentNode = dfNode[dfNode['id'].isin([content.string[1:6]])]
                            dfLink = dfLink.append(pd.DataFrame({'source':contentNode.iat[0,0], 'target':courseNode.iat[0,0], 'left':['false'], 'right':['true']}), ignore_index=True)
                if hissu != None:
                    for content in hissu.find_parent('tr').select('td:nth-of-type(2)')[0]:
                        if content.name == 'a' and content.string[1:6] in allId: 
                            contentNode = dfNode[dfNode['id'].isin([content.string[1:6]])]                            
                            dfLink = dfLink.append(pd.DataFrame({'source':contentNode.iat[0,0], 'target':courseNode.iat[0,0], 'left':['false'], 'right':['true']}), ignore_index=True)
    
tete = dfNode.to_json(orient='records', force_ascii=False)
toto = dfLink.to_json(orient='records')
output = '{{"nodes":{0},"links":{1}}}'.format(tete,toto)

with open('courses2.json', 'w') as f:
    f.write(output)