#!/usr/bin/python

#http://www.leancrew.com/all-this/2013/01/completing-my-twitter-archive/

from datetime import datetime
import pytz
import sys

# Universal convenience variables
utc = pytz.utc
instrp = '%Y-%m-%d %H:%M:%S +0000'
false = False
true = True

# Convenience variables specific to me
homeTZ = pytz.timezone('Asia/Shanghai')
urlprefix = 'http://twitter.com/drdrang/status/'
outstrf = '%Y-%m-%d %H:%M:%S'

# The list of JSON files to process is assumed to be given as
# the arguments to this script. They are also expected to be in
# chronological order. This is the way they come when the
# Twitter archive is unzipped.
for m in sys.argv[1:]:
  f = open(m)
  f.readline()            # discard the first line
  tweets = eval(f.read())
  tweets.reverse()        # we want them in chronological order
  for t in tweets:
    text = t['text']
    url = urlprefix + t['id_str']
    dt = utc.localize(datetime.strptime(t['created_at'], instrp))
    dt = dt.astimezone(homeTZ)
    date = dt.strftime(outstrf)
    print '''%s
%s
%s
- - - - -
''' % (text, date, url)

