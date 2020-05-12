# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 01:15:53 2017

@author: JackHsuan
heroku login
git init
heroku git:remote -a jackhsuanlinebot
git add .
git commit -am "make it better"
git push heroku master

"""
import requests
import json
import re
import random
import configparser
from selenium import  webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError, LineBotApiError
)
from linebot.models import *
import threading
import datetime
import time
import pymysql
import ast
import paho.mqtt.client as mqtt

_g_cst_MQTTSubClientID = "python_chsmSubClient"
_g_cst_MQTTPubClientID = "python_chsmPubClient"
_g_cst_MQTTPub2ClientID = "python_chsmPubPMClient"
Movie_group = 'C00cd9edf854598e80ea57e56b1241bf2'
JackHsuanLineID = 'U2c0fd74c8005427505431b35a67571ab'
Notify_token = 'gLI5gXpqVdNMX7x6UXMvawi4JZqXGl1WRALRRKUMoY7'#推播到電源耐久測試群組

def NtimeString():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

SSS = requests.session()

def brocast_by_Notify(token, msg):
	headers = {
		"Authorization": "Bearer " + token, 
		"Content-Type" : "application/x-www-form-urlencoded"
	}
	payload = {'message': msg}
	r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
	return r.status_code

def get_Mqtt(_clientID,type,userdata):
	_clientID = _clientID
	type = type
	userdata = userdata
	try:
		if(type =="Sub"):
			time.sleep(5)
			# print("Getmqtt_sub")
			client = mqtt.Client()			
			client.on_connect = on_connect
			client.on_message = on_message
			client.connect(_g_cst_ToMQTTTopicServerIP, _g_cst_ToMQTTTopicServerPort,60)
			client.loop_forever()
		else:
			pass
			# send_lineMessage(JackHsuanLineID,"get_mqtt異常，TypeError")
	except:
		time.sleep(10)
		# send_lineMessage(JackHsuanLineID,"get_mqtt異常，重新執行GetMqtt")
		get_Mqtt(_clientID,type,userdata)

def on_connect(client, userdata, flags, rc):
	print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" Connected with result code "+str(rc))
	# config.read("config.ini")
	# for i in config['device_time']:
	# 	client.subscribe("/v1/device/%s/sensor/TVOC/rawdata"%(i))
	client.subscribe("ntu_farm")

def on_message(client, userdata, msg):
	if(not msg.retain):
		topic = msg.topic
		message = str(msg.payload)
		print(NtimeString()+"現在線程數量"+str(threading.active_count()))
		MessageStr = 'From topic:'+topic+" data: "+str(message)
		threading.Thread(target = brocast_by_Notify,args = (Notify_token,MessageStr)).start()

def makeDict(Message):
	pattern = "({.*})"
	Message_String = str(Message)
	Message_Dict = ast.literal_eval(re.findall(pattern,Message_String)[0])
	return Message_Dict

def Check_permit(top):
	y_class = top.find_element_by_class_name("y")
	button_links = y_class.find_elements_by_tag_name('a')
	for link in button_links:
		if(link.text == '登錄' ):
			return 1
	return 0
		

def Get_Eyny_Movie():#抓取柳葉影片主題
	# -*- coding:utf-8 -*-
	try:
		print(NtimeString()+"starting try to get eyny movie")
		while(1):
			db = pymysql.connect(host =_db_Jhost, port =_db_Jport,user =_db_Juser, passwd =_db_Jpasswd,db =_db_Jdatabase)
			cursor = db.cursor()
			chrome_options = webdriver.ChromeOptions() 
			chrome_options.add_argument('--headless') # 啟動無頭模式 
			# chrome_options.add_argument('--disable-gpu')
			driver = webdriver.Chrome(chrome_options=chrome_options)
			time.sleep(5)
			driver.implicitly_wait(60)
			
			#登入
			driver.get("https://wee.eyny.com/member.php?mod=logging&action=login")
			time.sleep(5)
			# WebDriverWait(driver, 6000000, 0.5).until(EC.presence_of_element_located((By.ID,"nv_member")), print(NtimeString()+"get_request Time_out1"))
			username = driver.find_element_by_name("username")
			passwd = driver.find_element_by_name("password")
			username.clear
			passwd.clear
			username.send_keys(username)
			passwd.send_keys(passwd)
			button = driver.find_element_by_name('loginsubmit')
			button.click()
			time.sleep(5)
			#柳葉影片主題
			# driver.get("https://wee.eyny.com/home.php?mod=space&uid=13806978&do=thread&view=me&from=space")
			# table = driver.find_element_by_tag_name("table")
			# a_result = table.find_elements_by_tag_name("a")

			#電影下載區nv_forum
			driver.get("http://wee.eyny.com/forum.php?mod=forumdisplay&fid=205&filter=author&orderby=dateline")
			# table = driver.find_element_by_tag_name("table")
			a_result = driver.find_elements_by_tag_name("a")
			url_dict = {}
			# url_list = []
			for a in a_result:
				if(re.match("\[.\].*\(.*\)",a.text)):
					# print(a.text)
					url_dict[a.text] = a.get_attribute("href")
					# url_list.append(a.get_attribute("href"))
			#柳葉影片主題
			time.sleep(5)
			driver.get("https://wee.eyny.com/home.php?mod=space&uid=13806978&do=thread&view=me&from=space")
			table = driver.find_element_by_tag_name("table")
			a_result = table.find_elements_by_tag_name("a")
			for a in a_result:
				if(re.match("\[.\].*\(.*\)",a.text)):
					# print(a.text)
					url_dict[a.text] = a.get_attribute("href")
					# url_list.append(a.get_attribute("href"))
			# page_list = driver.find_element_by_class_name("pg").find_elements_by_tag_name("a")#頁數
			# del page_list[0]

			# print(url_dict)
			# print(url_list)
			# for i in url_list:
			for key in url_dict:
				try:
					while(Check_permit(driver)):
						# print("Check_permit = 1 有找到登陸按鈕")
						driver.get("https://wee.eyny.com/member.php?mod=logging&action=login")
						time.sleep(5)
						# WebDriverWait(driver, 6000000, 0.5).until(EC.presence_of_element_located((By.ID,"nv_member")), print(NtimeString()+"get_request Time_out1"))
						username = driver.find_element_by_name("username")
						passwd = driver.find_element_by_name("password")
						username.clear
						passwd.clear
						username.send_keys(username)
						passwd.send_keys(passwd)
						button = driver.find_element_by_name('loginsubmit')
						button.click()
						time.sleep(5)
						driver.get("https://wee.eyny.com/home.php?mod=space&uid=13806978&do=thread&view=me&from=space")
						time.sleep(5)
					# print("login_success")
					driver.get(url_dict[key])
					time.sleep(5)
					# WebDriverWait(driver, 6000000, 0.5).until(EC.presence_of_element_located((By.ID,"nv_forum")), print(NtimeString()+"get_request Time_out2"))
					froum_table = driver.find_element_by_class_name("t_fsz").find_element_by_tag_name('table')#定位到文章
					# print(table.text)
					movie_name = "Movie_name_idk"+str(random.randrange(0, 1000, 3))
					try:
						movie_name = froum_table.find_element_by_tag_name("font").text.split("：")[1]#找到電影名稱
					# print(movie_name)
					except:
						movie_name = key.split(']')[1].split(" ")[0]
					SqlCommand = "SELECT movie_name FROM %s.eyny WHERE movie_name ='%s'"%("jackhsuan",movie_name)
					result = cursor.execute(SqlCommand)
					if(result == 0):
						print(NtimeString()+"found_movie")
						print(NtimeString()+"key:"+key)
						print(NtimeString()+movie_name)
						SqlCommand = 'insert into %s.eyny(movie_name) values(\'%s\');'%("jackhsuan",movie_name)
						cursor.execute(SqlCommand)
						try:
							blockcode = froum_table.find_elements_by_class_name("blockcode")#找到blockcode
							print("find_blackcode")
							movie_url_list = []
							have_mega = 0
							have_google = 0 
							for b in blockcode:
								url = b.find_element_by_tag_name("li").text
								if(re.search("mega",url)):
									have_mega = 1
								if(re.search("google:",url)):
									have_google = 1
								movie_url_list.append(url)

							if(have_mega ==1 and have_google ==1):#去除mega如果有google drive
								for u in movie_url_list:
									if(re.match("mega",u)):
										movie_url_list.remove(u)
						except:
							print("cant find blockcode")
						try:
							find_links_in_table = froum_table.find_elements_by_tag_name("a")
							link_dict = {}
							for link in find_links_in_table:
								if(re.match(".*\.rar",link.text)):
									link_dict[""+link.text] = link.get_attribute("href")
								elif(re.search("mega",link.get_attribute("href"))):
									link_dict[""+link.text] = link.get_attribute("href")
								elif(re.search("drive.google",link.get_attribute("href"))):
									link_dict[""+link.text] = link.get_attribute("href")
								else:
									continue
						except:
							print("cant find a_href")
						# threading.Thread(target = send_lineMessage,args=(JackHsuanLineID,""+str(movie_name)+"鏈結"+str(movie_url_list))).start()
						# if(len(link_dict)!=0):
						# 	threading.Thread(target = send_lineMessage,args=(JackHsuanLineID,""+str(movie_name)+"未知用途鏈結"+str(link_dict))).start()
						threading.Thread(target = send_lineMessage,args=(Movie_group,""+str(key)+"鏈結\n"+str(movie_url_list)+"\n來源：\n"+str(url_dict[key]))).start()
						if(len(link_dict)!=0):
							threading.Thread(target = send_lineMessage,args=(Movie_group,""+str(key)+"未知用途鏈結\n"+str(link_dict))).start()
						db.commit()
					else:
						continue
				except:
					continue
			try_logout = driver.find_elements_by_tag_name("a")
			for butt in try_logout:
				if(re.match("退出",butt.text)):
					butt.click()
					print("登出")
					break
			driver.close()
			db.close()
			time.sleep(1800)
	except:	
		driver.close()
		db.close()
		time.sleep(600)
		Get_Eyny_Movie()

def Get_Trial_key():
	# -*- coding:utf-8 -*-
	try:
		EsetUrl = "http://nodhk.me/"
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
		headers = { 'User-Agent' : user_agent }

		ESETPAGE = SSS.get(EsetUrl,headers=headers)
	#	 print (ESETPAGE.text)
		soup = BeautifulSoup(ESETPAGE.text,"html.parser")
		result = soup.find_all('input')
	#	 print(result)
		pattern1 = r"[0-9|a-z]{10}"
		pattern2 = r"[A-Z]{5}\-[0-9]{10}"
		pattern3 = r"[0-9|A-Z]{4}\-[0-9|A-Z]{4}\-[0-9|A-Z]{4}\-[0-9|A-Z]{4}\-[0-9|A-Z]{4}"
		message = ""
		for v in result:
			r = v.get('value')
	#		 re.match(pattern1, str(r)))
			if(re.match(pattern1,str(r))!=None):
				message = message+"密碼:"+str(r)+'\n'
			if(re.match(pattern2,str(r))!=None):
				message = message+"帳號:"+str(r)+'\n'
			if(re.match(pattern3,str(r))!=None):
				message = message+"序號:"+str(r)+'\n'

		return message

	except TypeError:
		return "請聯絡軒"
	except:
		return "未知錯誤 請聯絡軒"

def Get_Movie():
	try:
		MovieUrl = "http://www.atmovies.com.tw/movie/now/"
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
		headers = { 'User-Agent' : user_agent }

		MoviePage = SSS.get(MovieUrl,headers=headers,allow_redirects = False)
		MoviePage.encoding = 'utf-8'
		soup = BeautifulSoup(MoviePage.text,"lxml")
		result = soup.find('ul',class_='filmListAll2').find_all('li')
		Movie_list = ""
		for i in result:
			Url_Text = i.find('a')
			Movie_list = Movie_list+ Url_Text.text+"\n"+"http://www.atmovies.com.tw/"+Url_Text['href']+"\n"+"網路評分(分數/評分人數)："+i.find('div',id="listAllRating").text+"\n"
		return Movie_list[:2000]
	except :
		return "未知錯誤 請聯絡軒"

def movie():
	target_url = 'http://www.atmovies.com.tw/movie/next/'
	print('Start parsing movie ...')
	res = SSS.get(target_url, verify=False)
	res.encoding = 'utf-8'
	soup = BeautifulSoup(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('ul.filmNextListAll2 a')):
		if index == 20:
			return content
		title = data.text.replace('\t', '').replace('\r', '')
		link = "http://www.atmovies.com.tw" + data['href']
		content += '{}\n{}\n'.format(title, link)
	return content

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
username = config['crawler']['username']
passwd = config['crawler']['passwd']
_db_Jhost = config['mysql']['jhost']
_db_Jport = int(config['mysql']['jport'])
_db_Juser = config['mysql']['juser']
_db_Jpasswd = config['mysql']['jpasswd']
_db_Jdatabase = config['mysql']['jdatabase']
_g_cst_ToMQTTTopicServerIP = config['Mqtt']['MQTTTopicServerIP']
_g_cst_ToMQTTTopicServerPort = int(config['Mqtt']['port'])

# @app.route("/download/<filename>", methods=['GET'])
# def download_file(filename):
# # 需要知道2個引數, 第1個引數是本地目錄的path, 第2個引數是檔名(帶副檔名)
# 	directory = os.getcwd()  # 假設在當前目錄
# 	print(directory)
# 	response = make_response(send_from_directory(directory, filename, as_attachment=True))
# 	print(response)
# 	response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
# 	print(response)
# 	return response
@app.route("/cq/",methods=['GET'])
def CQ_brocast():
	token = request.args['tk']
	msg = request.args['msg']
	print(token,msg)

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	# print("body:",body)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'ok'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	sourceStr = str(event.source)
	sourceStr = sourceStr.split("userId\":")
	EuserID = sourceStr[1][2:-2]
	print("event.reply_token:", event.reply_token)
	print("event.message.text:", event.message.text)
	event_dict = makeDict(str(event))
	event_type = event_dict['source']['type']
	# print("event.reply_token:", event.reply_token)
	# print("event.message.text:", event.message.text)
	event_reply_to_who = ""
	if(event_type == 'group'):
		event_reply_to_who = event_dict['source']['groupId']
	elif(event_type == 'user'):
		event_reply_to_who = event_dict['source']['userId']
	else:
		print("event_type Error")
	print(event_reply_to_who)
	if event.message.text == "eset" or event.message.text =="Eset" or event.message.text == "ESET":
		content = Get_Trial_key()
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=content))
		return 0

	if event.message.text == "movie" or event.message.text =="Movie" or event.message.text == "MOVIE":
		content = Get_Movie()
		# print(content)
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=content))
		return 0
	if event.message.text == "eyny":
		print("get_message: eyny")
		threading.Thread(target = Get_Eyny_Movie).start()
		# eyny_movie_dict = Get_Eyny_Movie()
		# for key in eyny_movie_dict:
		# 	send_lineMessage(JackHsuanLineID,""+str(key)+str(eyny_movie_dict[key]))
	if event.message.text == "即將上映電影":
		content = movie()
		reply_lineMessage(event.reply_token,content)
		# line_bot_api.reply_message(
		# 	event.reply_token,
		# 	TextSendMessage(text=content))
		return 0
	if re.match("preserve",event.message.text):
		threading.Thread(target = second_job,args=(EuserID,event.message.text)).start()
		message = event.message.text.split(",")
		send_lineMessage(EuserID,message[4])
		# print("Ending thread")
		return 0
	# if(re.match("car",event.message.text)):
	# 	threading.Thread(target = submit_car).start()

def reply_lineMessage(reply_token,replystring):
	line_bot_api.reply_message(
			reply_token,
			TextSendMessage(text=replystring))

def send_lineMessage(LineAtUserID,timestr):
	print("Sending Message")
	line_bot_api.push_message(LineAtUserID, TextSendMessage(text=timestr))

threading.Thread(target = Get_Eyny_Movie).start()
# threading.Thread(target = submit_car).start()
threading.Thread(target = get_Mqtt,args = (_g_cst_MQTTSubClientID,"Sub",None)).start()

if __name__ == '__main__':
	app.run()

# tm_year=2016, tm_mon=4, tm_mday=7, 
# tm_hour=10, tm_min=28, tm_sec=49, 

def second_job(EuserID,message):
	print("Second_job Start")
	message = message.split(",")
	dt = datetime.datetime.now()
	pushtime = dt + datetime.timedelta(days = int(message[1]),hours = int(message[2]),seconds = int(message[3]))
	# print("dt = "+dt)
	# print("pushtime = "+pushtime)
	# send_lineMessage(EuserID,message[4])
	while 1:
		# print(datetime.datetime.now())
		# time_tup = time.localtime(time.time())
		if datetime.datetime.now() == pushtime:
			send_lineMessage(EuserID,message[4])
			break


# def main():
	# 添加一個 thread 
	# first_thread = threading.Thread(target=thread_job)
	# 執行 thread
	# first_thread.start() # This is an added Thread, number is <Thread(Thread-1, started 123145466363904)>
	# 看目前有幾個 thread
	# print(threading.active_count()) # 2
	# 把所有的 thread 顯示出來看看
	# print(threading.enumerate()) # [<_MainThread(MainThread, started 140736627270592)>, <Thread(Thread-1, started 123145466363904)>]
	# 把目前的 thread 顯示出來看看
	# print(threading.current_thread()) #<_MainThread(MainThread, started 140736627270592)>
