#!/usr/bin/python3
# -*- coding:utf-8 -*-

from datetime import datetime,timezone,timedelta
import sys

instrp = '%Y-%m-%d %H:%M:%S +0000'
outstrf = '%Y-%m-%d %H:%M:%S CST UTC+08:00'
urlprefix = 'https://twitter.com/litanid/status/'
false = False
true = True

for m in sys.argv[1:]:
	fl = open(m)
	fl.readline()
	tweets = eval(fl.read())
	tweets.reverse()
	print(r"####**本次归档共计 {0} 条推文：**".format(len(tweets)))
	print("---")
	for lt in tweets :
		created_at = lt['created_at']
		dt = datetime.strptime(created_at, instrp)
		dt = dt.replace(tzinfo=timezone.utc)
		tzutc_8 = timezone(timedelta(hours=8))
		local_dt = dt.astimezone(tzutc_8)
		local_dt = local_dt.strftime(outstrf)
		url = urlprefix + lt['id_str']
		ltweetext = lt['text'].replace('\\','')				#删掉推文里网址里多余的'\'字符
		ltweetext = ltweetext.encode(encoding='utf-8',errors='xmlcharrefreplace')		#过滤掉不能解码的特殊字符，用&#xxxx表示
		#ltweetext = ltweetext.encode(encoding='utf-8',errors='backslashreplace')		#过滤掉不能解码的特殊字符，用\uxxxx表示
		ltweetext = ltweetext.decode()
		print(ltweetext)
		#print("[{0}]".format(local_dt),end='')
		#print("({0})".format(url),end='')
		print("<br /><a href='{0}' target=\"_blank\">{1}</a>".format(url,local_dt))
		print("---")
	fl.close()
