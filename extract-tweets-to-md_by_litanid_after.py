#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
extract-tweets-to-md
by Marcin Wichary (aresluna.org)

Site: https://github.com/litanid/extract-tweets


本程序请使用 Python3 运行。实现功能是提取推待官方存档 json 文件信息输出保存
为 markdown 文件，同时下载推文中涉及到的所有图片和视频保存到当前目录下的新建
目录。要求程序目录下有诸如 2017_10.js 等格式文件。
在终端下运行此文件，如“python3 extract-tweets-to-md.py 2017_10.js”命令，后面
可接多个 .js 文件，则输出markdown文件为同目录下的 2017_10.md ，相应的图片和
视频下载到201710目录下。


下载视频代码最好还是要修改一下。


如果推文太长，被截取了，可否获取全文
'''

from datetime import datetime,timezone,timedelta
import sys
import re
import json
import os
import termios  #实现按任意键退出

if (sys.version_info > (3, 0)):
	from urllib.request import urlretrieve
else:
	from urllib import urlretrieve

#实现按任意键退出或继续
def press_any_key_exit(msg):
    # 获取标准输入的描述符
    fd = sys.stdin.fileno()

    # 获取标准输入(终端)的设置
    old_ttyinfo = termios.tcgetattr(fd)

    # 配置终端
    new_ttyinfo = old_ttyinfo[:]

    # 使用非规范模式(索引3是c_lflag 也就是本地模式)
    new_ttyinfo[3] &= ~termios.ICANON
    # 关闭回显(输入不会被显示)
    new_ttyinfo[3] &= ~termios.ECHO

    # 输出信息
    sys.stdout.write(msg)
    sys.stdout.flush()
    # 使设置生效
    termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
    # 从终端读取
    os.read(fd, 7)

    # 还原终端设置
    termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)

#删除重复元素
def dedupe(items, key=None):
	seen = set()
	for item in items:
		val = item if key is None else key(item)
		if val not in seen:
			yield item
			seen.add(val)

#instrp = '%Y-%m-%d %H:%M:%S +0000'		#对应如  2017-12-31 15:15:15 +0000
instrp = '%a %b %d %H:%M:%S +0000 %Y'	#对应如  Wed Nov 29 15:37:26 +0000 2017
'''
		存档推文日期时间格式，根据实际修改：
		%a　　本地（locale）简化星期名称				%A　　本地完整星期名称
		%b　　本地简化月份名称							%B　　本地完整月份名称
		%c　　本地相应的日期和时间表示					%d　　一个月中的第几天（01 - 31）
		%H　　一天中的第几个小时（24小时制，00 - 23）		%I　　第几个小时（12小时制，01 - 12）
		%j　　一年中的第几天（001 - 366）				%m　　月份（01 - 12）
		%M　　分钟数（00 - 59）						%p　　本地am或者pm的相应符
		%S　　秒（01 - 61）
		%U　　一年中的星期数。（00 - 53星期天是一个星期的开始。）第一个星期天之前的所有天数都放在第0周。
		%w　　一个星期中的第几天（0 - 6，0是星期天）		%W　　和%U基本相同，不同的是%W以星期一为一个星期的开始。
		%x　　本地相应日期								%X　　本地相应时间
		%y　　去掉世纪的年份（00 - 99）					%Y　　完整的年份
		%Z　　时区的名字（如果不存在为空字符）			%%　　‘%’字符
'''

outstrf = '%Y-%m-%d %H:%M:%S CST UTC+08:00'
urlprefix = 'https://twitter.com/litanid/status/'
outputFile_extension = '.md'
images_vedio_urlprefix = 'https://pich.yiwan.pro/YiWan/TwitterPictures/'

for month_tweets_filename in sys.argv[1:]:
	#取得输出文件的文件名和扩展名
	outputFile_name = ''		#清空重置文件名
	outputFile_name = os.path.basename(month_tweets_filename)
	outputFile_name_temp = outputFile_name
	outputFile_name = os.path.splitext(outputFile_name)[0]
	outputFile_name = outputFile_name + outputFile_extension
	print("\n====================处理文件 {0} ====================\n".format(outputFile_name_temp))
	print("##############\n输出文件名为同目录下的 {} 。".format(outputFile_name))

	tweet_image_total_count = 0
	tweet_video_total_count = 0
	tweet_image_failure_count = 0
	tweet_video_failure_count = 0

	
	with open(month_tweets_filename) as data_file:
		data_str = data_file.read()
		first_data_line = re.match(r'Grailbird.data.tweets_(.*) =', data_str).group(0)
		data_str = re.sub(first_data_line, '', data_str)
		data_tweets = json.loads(data_str)

	data_tweets.reverse() 

	with open(outputFile_name,'w') as outputFile:
		print(r"####**本次归档共计 {0} 条推文：**".format(len(data_tweets)),file = outputFile)
		print("本次归档共计 {0} 条推文：\n##############".format(len(data_tweets)))
		print("---",file = outputFile)

		for tweet in data_tweets :
			#处理日期时间显示格式，原时间格式为格林尼治时间，转为北京东八区时间
			created_at = tweet['created_at']
			dt = datetime.strptime(created_at, instrp)
			dt = dt.replace(tzinfo=timezone.utc)
			tzutc_8 = timezone(timedelta(hours=8))
			local_dt = dt.astimezone(tzutc_8)
			local_dt = local_dt.strftime(outstrf)
			local_datetime = local_dt[:19]
			datetime_number = re.sub(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)',r'\1\2\3\4\5\6',local_datetime)


			tweetlink_url = urlprefix + tweet['id_str']

			tweet_text = tweet['text']
			#如果text中有网址，则替换成实际应该显示的网址
			try:
				if tweet['entities']['urls']:
					for replaceurl in tweet['entities']['urls']:
						url = replaceurl['url']
						expanded_url = replaceurl['expanded_url']
						display_url = replaceurl['display_url']
						display_url = "<a href='" + expanded_url + "' target=\"_blank\">" + display_url + "</a>"
						tweet_text = re.sub(url, display_url, tweet_text)
			except KeyError:
				pass

			print(tweet_text,file = outputFile)
			print("\n---------------------------------------")
			print("{0} 发布推文：\n\t{1}".format(local_datetime,tweet_text))


			#建立以年月为名称的文件夹用来保存当月的图片和视频
			media_directory_name = datetime_number[:6]
			if not os.path.isdir(media_directory_name):
				os.mkdir(media_directory_name)

			medialist = []
			tweet_image_count = 0
			tweet_video_count = 0

			try:
				if 'extended_entities' in tweet.keys() and 'media' in tweet['extended_entities'].keys(): 
					medialist.extend(tweet['extended_entities']['media'])
				if 'retweeted_status' in tweet.keys() and 'extended_entities' in tweet['retweeted_status'].keys() \
					and 'media' in tweet['retweeted_status']['extended_entities'].keys():
					medialist.extend(tweet['retweeted_status']['extended_entities']['media'])
					
				medialist = list(dedupe(medialist, key=lambda d: d['media_url_https']))
				
				for media in medialist:
					if media['type']=="photo" :
						media_url_https = media['media_url_https']
						media_filename = os.path.basename(media_url_https)
						# Download the original/best image size, rather than the default one
						better_media_url_https = media_url_https + ':orig'
						local_media_filename = '%s/%sX%s%sH%s' %\
							(media_directory_name, datetime_number, tweet['id'], tweet_image_count+1, media_filename)
						if os.path.isfile(local_media_filename):
							print("\t*********已经下载过这张图片{0}，此处略过！".format(media_url_https))
							local_media_filename = images_vedio_urlprefix + local_media_filename
							print("<br /><a href='{0}'><img class='alignnone size-medium' src='{1}'  /></a>".format(local_media_filename,local_media_filename),file = outputFile)
							tweet_image_count = tweet_image_count + 1
							tweet_image_total_count = tweet_image_total_count + 1
						else:
							print("\t*********下载第{0}张图片：{1}".format(tweet_image_count+1,media_url_https))
							try:
								urlretrieve(better_media_url_https, local_media_filename)
							except:
								print("\t*********第{0}张图片（{1}）下载失败！！".format(tweet_image_count+1,media_url_https))
								tweet_image_failure_count = tweet_image_failure_count + 1
								pass
							else:
								local_media_filename = images_vedio_urlprefix + local_media_filename
								print("<br /><a href='{0}'><img class='alignnone size-medium' src='{1}'  /></a>".format(local_media_filename,local_media_filename),file = outputFile)
								tweet_image_count = tweet_image_count + 1
								tweet_image_total_count = tweet_image_total_count + 1
								print("\t*********第{0}张图片（{1}）下载成功！！".format(tweet_image_count,media_url_https))

					elif media['type']=="video" :
						media_image_url_https = media['media_url_https']
						media_image_filename = os.path.basename(media_image_url_https)
						# Download the original/best image size, rather than the default one
						better_media_image_url_https = media_image_url_https + ':orig'
						local_media_image_filename = '%s/%sX%s%sH%s' %\
							(media_directory_name, datetime_number, tweet['id'], tweet_image_count+1, media_image_filename)
						if os.path.isfile(local_media_image_filename):
							print("\t*********已经下载过这张视频封面图{0}，此处略过！".format(media_image_url_https))
							local_media_image_filename = images_vedio_urlprefix + local_media_image_filename
							tweet_image_count = tweet_image_count + 1
							tweet_image_total_count = tweet_image_total_count + 1
						else:
							print("\t*********下载第{0}张图片：{1}".format(tweet_image_count+1,media_image_url_https))
							try:
								urlretrieve(better_media_image_url_https, local_media_image_filename)
							except:
								print("\t*********第{0}张图片（{1}）下载失败！！".format(tweet_image_count+1,media_image_url_https))
								tweet_image_failure_count = tweet_image_failure_count + 1
								pass
							else:
								local_media_image_filename = images_vedio_urlprefix + local_media_image_filename
								tweet_image_count = tweet_image_count + 1
								tweet_image_total_count = tweet_image_total_count + 1
								print("\t*********第{0}张图片（{1}）下载成功！！".format(tweet_image_count,media_image_url_https))

						video_quality_temp = []
						for video_quality in media['video_info']['variants'] :
							if "bitrate" in video_quality :
								video_quality_temp.append(video_quality)
							else :
								continue
						aftersorted_video_quality=sorted(video_quality_temp,key=lambda quality:quality['bitrate'],reverse=True)
						better_media_video_url_https = aftersorted_video_quality[0]['url']
						better_media_video_filename = os.path.basename(better_media_video_url_https)
						local_media_video_filename = '%s/%sX%s%sH%s' %\
							(media_directory_name, datetime_number, tweet['id'], tweet_video_count+1, better_media_video_filename)
						if os.path.isfile(local_media_video_filename):
							print("\t*********已经下载过这个视频{0}，此处略过！".format(better_media_video_url_https))
							local_media_video_filename = images_vedio_urlprefix + local_media_video_filename
							tweet_video_count = tweet_video_count + 1
							tweet_video_total_count = tweet_video_total_count + 1
							print("\n<video src='{0}' controls autoplay loop>  Your browser does not support the <code>video</code> element.</video>\n"\
									.format(local_media_video_filename),file = outputFile)
						else:
							print("\t*********下载第{0}个视频：{1}".format(tweet_video_count+1,better_media_video_url_https))
							try:
								urlretrieve(better_media_video_url_https, local_media_video_filename)
							except:
								print("\t*********第{0}个视频（{1}）下载失败！！".format(tweet_video_count+1,better_media_video_url_https))
								tweet_video_failure_count = tweet_video_failure_count + 1
								pass
							else:
								print("\t*********第{0}个视频（{1}）下载成功！！".format(tweet_video_count+1,better_media_video_url_https))
								local_media_video_filename = images_vedio_urlprefix + local_media_video_filename
								tweet_video_count = tweet_video_count + 1
								tweet_video_total_count = tweet_video_total_count + 1
								print("\n<video src='{0}' controls autoplay loop>  Your browser does not support the <code>video</code> element.</video>\n"\
									.format(local_media_video_filename),file = outputFile)
			except KeyError:
				pass

			print("<br /><a href='{0}' target=\"_blank\">{1}</a>".format(tweetlink_url,local_dt),file = outputFile)
			print("---",file = outputFile)
			print("---------------------------------------")
	print("\n##############")
	print("\n本次归档共计成功下载{0}张图片、{1}个视频，下载失败{2}张图片、{3}个视频！".\
		format(tweet_image_total_count,tweet_video_total_count,tweet_image_failure_count,tweet_video_failure_count))
	print("\n##############")
	print("\n====================文件 {0} 处理完毕====================\n".format(outputFile_name_temp))

press_any_key_exit("程序运行结束！请将图片和视频目录拷贝至相应图片库后再打开生成文件浏览！\n请按任意键退出...\n")