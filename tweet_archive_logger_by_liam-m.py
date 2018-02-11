#https://github.com/liam-m/TweetArchiveLogger

import csv

username = 'litanid'
csv_path = '/home/litanid/litanid_Temporary/tweets.csv'
output_path = '/home/litanid/litanid_Temporary/tweets.md.txt'

tweet_format = '''
{{text}}

[{{date}}]({{url}})

---

'''

date_format = '{{month}} {{day}}, {{year}} at {{hour_12}}:{{minute}}{{am}}'



def get_12_hour(hour):
	if int(hour) in [0, 12]:
		return '12'
	elif int(hour) > 12:
		hour = str(int(hour) - 12)
        while len(hour) < 2:
                hour = '0' + hour
        return hour

def get_month(n):
        d = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
             6: "June", 7: "July", 8: "August", 9: "September", 10: "October",
             11: "Novermber", 12: "December"}
        return d.get(n) # None if n not in range 1-12

def format_date(date, format):
	year = date[:4]
	month = date[5:7]
	day = date[8:10]
	hour = date[11:13]
	minute = date[14:16]
	second = date[17:19]
	am = "AM" if int(hour) < 12 else "PM"
	hour12 = get_12_hour(hour)
	
	out = format
	out = out.replace("{{year}}", year)
	out = out.replace("{{month_num}}", month)
	out = out.replace("{{month}}", get_month(int(month)))
	out = out.replace("{{month_short}}", get_month(int(month))[0:3])
	out = out.replace("{{day}}", day)
	out = out.replace("{{hour}}", hour)
	out = out.replace("{{hour_12}}", get_12_hour(hour))
	out = out.replace("{{minute}}", minute)
	out = out.replace("{{second}}", second)
	out = out.replace("{{am}}", am)
	
	return out
	

def format_tweet(tweet, format):
	tweet_id = 0
	in_reply_to_status_id = 1
	in_reply_to_user_id = 2
	timestamp = 3
	source = 4
	text = 5
	retweeted_status_id = 6
	retweeted_status_user_id = 7
	retweeted_status_timestamp = 8
	expanded_urls = 9
	
	base_url = 'http://twitter.com/' + username + '/status/'
	
	out = format
	out = out.replace("{{id}}", tweet[tweet_id])
	out = out.replace("{{date}}", format_date(tweet[timestamp], date_format))
	out = out.replace("{{text}}", tweet[text])
	out = out.replace("{{url}}", base_url + tweet[tweet_id])
	
	return out

output = ''

with open(csv_path, 'rb') as csvfile:
	reader = csv.reader(csvfile)
	for row in reversed(list(reader)):
		if (row[0] != "tweet_id"):
			output += format_tweet(row, tweet_format)

output_file = open(output_path, 'wb')
output_file.write(output)
output_file.close()
