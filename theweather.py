import twython
import time
import re
import urllib2,json
from xml.dom import minidom
import cPickle

try:
	from settings import TWITTER_USERNAME, TWITTER_PASSWORD, YAHOO_APP_ID
except ImportError:
	TWITTER_USERNAME, TWITTER_PASSWORD, YAHOO_APP_ID = '','',''

DELAY_TIME = 30 # Time in seconds to delay queries to the twitter api
YAHOO_WOEID_URL = "http://where.yahooapis.com/v1/places.q('%s')?format=json&appid=%s"
YAHOO_FORECAST_URL = "http://weather.yahooapis.com/forecastrss?w=%s&u=f"
YAHOO_WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
DUMP_FILE = 'dump_file.txt'
zipcode_re = re.compile('(?P<zipcode>\d\d\d\d\d)')


def main():
	twitter = twython.core.setup(username=TWITTER_USERNAME, password=TWITTER_PASSWORD)
	zipcode = ''
	try:
		with open(DUMP_FILE,'r') as dump_file:
			since = cPickle.load(dump_file)	
	except IOError:
		since = None
	try:
		while True:
			if since:
				mentions = twitter.getUserMentions(since_id=since)
			else:
				mentions = twitter.getUserMentions()
			for mention in mentions:
				text = mention['text']
				screen_name = mention['user']['screen_name']
				matched = zipcode_re.search(text)
				try:
					zipcode = matched.group('zipcode')
				except IndexError:
					zipcode = None
				woeid = getWOEID(zipcode)
				text,temp = getCurrentWeather(woeid)
				twitter.updateStatus("@%(screen_name)s It is %(text)s and %(temp)sF in %(zipcode)s" % locals())
			try:
				since = mentions[-1]['id']
			except IndexError:
				since = None
			time.sleep(DELAY_TIME)
	except KeyboardInterrupt:
		with open(DUMP_FILE,'w') as dump_file:
			cPickle.dump(since, dump_file)
					
		raise
		
def getCurrentWeather(woeid):
	data = minidom.parse(urllib2.urlopen(YAHOO_FORECAST_URL % woeid))
	condition = data.getElementsByTagName('yweather:condition')[0]
	return condition.getAttribute('text'),condition.getAttribute('temp')
	
def getWOEID(location):
	data = json.loads(urllib2.urlopen(YAHOO_WOEID_URL % (location,YAHOO_APP_ID)).read())
	try:
		woeid = data['places']['place'][0]['woeid']
	except KeyError:
		woeid = None
	return woeid
	
if __name__ == '__main__':
	main()