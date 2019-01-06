
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
