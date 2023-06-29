import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import gspread
from google.oauth2.service_account import Credentials
p=28 #爬的頁數

def funtime(url,page):
  url= url+str(page)
  response=requests.get(url,headers={
      "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
  })
  text=BeautifulSoup(response.text,'html.parser')
  title=text.find_all("div", class_="ticket_right")
  title_l=text.find_all("div", class_="ticket_left")
  link=[]
  coupon=[]
  tag=[]
  price=[]
  source=[]
  description=[]
  region=[]
  for info in title:
    detail=info.find("div",class_="ticket_right_box").a
    link.append(detail['href'])
    coupon.append(detail['data-title'])
    source.append(detail['data-source'])
    price.append(detail['data-price'])
    region.append(detail['data-region'])
    description.append(info.find("div",class_="shorten_url")["data-share_text"])
  #tag.append(info.find("div",class_="ticket_icon_row").text)
  for info in title_l:
    tag.append(info.find("div",class_="ticket_icon").text.replace('\n',''))
  data=pd.DataFrame({
  '名稱':coupon, '價格':price,'所在地':region, '描述':description,'標籤':tag, '來源':source,'連結':link
  })
  return data 
url="https://www.funtime.com.tw/localtour/city.php?target=RE_TAIWAN&cat=food&subcat=&order=hot&page="
page=1
data=funtime(url,page)
pbar=tqdm(total=p)
for i in range(1,p+1):
  page=i
  add=funtime(url,page)
  if page!=1:
    data=pd.concat([data,add],axis=0)
  else:
    data=add
  pbar.update(1)
pbar.close()
data=data.reset_index()
data=data.drop('index',axis=1)

scope=['https://www.googleapis.com/auth/spreadsheets']
cred=Credentials.from_service_account_file("./ccclub-391308-cd917d9d58fa.json",scopes=scope)
gs=gspread.authorize(cred)
final=gs.open_by_url('https://docs.google.com/spreadsheets/d/1Z2UrLq5K7nM0XQNmRdKXS3EKm5PPHig5TPdSYx8ljB0/edit#gid=0')
Worksheet=final.get_worksheet(0)

Worksheet.update([data.columns.values.tolist()]+data.values.tolist())
new_df = pd.DataFrame(Worksheet.get_all_records())
print(new_df)