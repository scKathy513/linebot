from flask import Flask, request, abort

import urllib.request, json
import requests
from bs4 import BeautifulSoup

import os
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

ACCESS_TOKEN= os.environ['ACCESS_TOKEN']
SECRET= os.environ['CHANNEL_SECRET']

# Channel Access Token
line_bot_api = LineBotApi(ACCESS_TOKEN)
# Channel Secret
handler = WebhookHandler(SECRET)

pm_site = {}

@app.route("/")
def hello_world():
    return "hello world!"


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
#     _message = TextSendMessage(text='Nice to meet you!')
#     _message = TextSendMessage(text=(event.source.user_id)) #reply userid
#     line_bot_api.reply_message(event.reply_token, _message)  
    # message = TextSendMessage(text=event)
#     print(event)

    msg = event.message.text
    _low_msg = msg.lower()
    
    _token = msg.strip().split(" ")
    _low_token = _token[0].lower()
    
    # query THU courses
    if '課程' in _token[0] or '課表' in _token[0]:
        cls_list = getCls(_token[1])
        for cls in cls_list:
            _message = TextSendMessage(text=cls)	#reply course
            line_bot_api.reply_message(event.reply_token, _message)
#            line_bot_api.push_message(event.source.user_id, TextSendMessage(text='123'))
    elif '誠品' in _token[0] or '書單' in _token[0]:
        bookls = find_bookls(_token[1])
        _message = TextSendMessage(text=bookls)	#reply course
        line_bot_api.reply_message(event.reply_token, _message)
    elif '空氣' in _token[0] or 'pm2' in _low_token:
        # query PM2.5
        for _site in pm_site:
            if _site == _token[1]:
                _message = TextSendMessage(text=pm_site[_site]) #reply pm2.5 for the site
                line_bot_api.reply_message(event.reply_token, _message)
                break;
    else:
        search_result = get_search_engine(_token[0], 3)
        reply = "您所搜尋的結果為：\n"
        #line_bot_api.reply_message(event.reply_token,reply)
        for r in search_result:
            result_message = r[0] + "("+r[1]+")"
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text=result_message))
	
def find_bookls(kw):
    with open("ESLITE.json",'r') as load_f:
        load_dict = json.load(load_f)
    x = load_dict['items']
    ans = ()
    for i in x:
        #if i['title'] == "title":
        if i['title'].find(str(kw))== -1:
            pass
#             print("")
        else:
            ans= (i['title']+i['link'])
#             print (i['title'], i['link'])
    return ans

def loadPMJson():
    with urllib.request.urlopen("http://opendata2.epa.gov.tw/AQX.json") as url:
        data = json.loads(url.read().decode())
        for ele in data:
            pm_site[ele['SiteName']] = ele['PM2.5']

def getCls(cls_prefix):
    ret_cls = []
    urlstr = 'https://course.thu.edu.tw/search-result/107/1/'
    postfix = '/all/all'
    
    qry_cls = urlstr + cls_prefix + postfix
    
    resp = requests.get(qry_cls)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    clsrooms = soup.select('table.aqua_table tbody tr')
    for cls in clsrooms:
        cls_info = cls.find_all('td')[1]
        cls_name = cls_info.text.strip()
        sub_url = 'https://course.thu.edu.tw' + cls_info.find('a')['href']
        ret_cls.append(cls_name + " " + sub_url)
        break
#         ret_cls = ret_cls + sub_url + "\n"

    return ret_cls

# 爬搜尋引擎，預設爬回傳4筆
def get_search_engine(search_thing, result_num=4):
    result = []
    target_url = 'https://www.bing.com/search'
    target_param = urllib.parse.urlencode({'q':search_thing}) # Line bot 所接收的關鍵字 !!!!
    target = target_url + '?' + target_param
    r = requests.get(target)
    html_info = r.text # 抓取 HTML 文字
    soup = BeautifulSoup(html_info, 'html.parser')
    search_result = soup.find('ol', {'id': 'b_results'}) #搜尋所有結果
    search_result_li = search_result.find_all('li', {'class':'b_algo'}) # 每一則的結果
    for idx, li in enumerate(search_result_li):
        if idx < result_num:
            target_tag = li.find('h2').find('a') # 每一則的超連結
            title = target_tag.get_text() # 每一則的標題
            href= target_tag['href'] # 每一則的網址
            result.append((title, href))
    return result
              
          
            
import os
if __name__ == "__main__":
    # load PM2.5 records
    #loadPMJson()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
#更

# 查詢高鐵時刻：http://www.thsrc.com.tw/tw/TimeTable/SearchResult
# 台北→台南, 2017/11/30, 5:30後啟程的班車

import requests
from bs4 import BeautifulSoup

url = 'http://www.thsrc.com.tw/tw/TimeTable/SearchResult'

# 找到option值
form_data = {
    'StartStation':'977abb69-413a-4ccf-a109-0272c24fd490',
    'EndStation':'9c5ac6ca-ec89-48f8-aab0-41b738cb1814',
    'SearchDate':'2017/11/30',
    'SearchTime':'05:30',
    'SearchWay':'DepartureInMandarin'
}

# 用request.post，並放入form_data
response_post = requests.post(url, data=form_data)

soup_post = BeautifulSoup(response_post.text, 'lxml')
soup_post
# 所有班車(train_number)
td_col1 = soup_post.find_all('td', {'class':'column1'})
train_numbers = []

for tag in td_col1:
    # print(tag)
    train_number = tag.text
    train_numbers.append(train_number)
    
print(train_numbers)

# 所有出發時間(departure_time)
td_col3 = soup_post.find_all('td', {'class':'column3'})
departure_times = []

for tag in td_col3:
    departure_time = tag.text
    departure_times.append(departure_time)
    
print(departure_times)

# 所有到達時間(arrival_time)
td_col4 = soup_post.find_all('td', {'class':'column4'})
arrival_times = []

for tag in td_col4:
    arrival_time = tag.text
    arrival_times.append(arrival_time)
    
print(arrival_times)

# 所有行車時間(travel_time)
td_col2 = soup_post.find_all('td', {'class':'column2'})
travel_times = []

for tag in td_col2:
    travel_time = tag.text
    travel_times.append(travel_time)
    
print(travel_times)

# 整理成表格
import pandas as pd

highway_df = pd.DataFrame({
    '車次': train_numbers,
    '出發時間': departure_times,
    '到達時間': arrival_times,
    '行車時間': travel_times},
    columns = ['車次', '出發時間', '到達時間', '行車時間'])

highway_df
