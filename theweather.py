import twython
import time
import re
import urllib2,json
from xml.dom import minidom

TWITTER_USERNAME = '[username]'
TWITTER_PASSWORD = '[password]'
YAHOO_APP_ID = '[YAHOO_APP_ID]'
YAHOO_WOEID_URL = "http://where.yahooapis.com/v1/places.q('%s')?format=json&appid=%s"
YAHOO_FORECAST_URL = "http://weather.yahooapis.com/forecastrss?w=%s&u=f"
YAHOO_WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
zipcode_re = re.compile('(?P<zipcode>\d\d\d\d\d)')

def main():
	twitter = twython.core.setup(username=TWITTER_USERNAME, password=TWITTER_PASSWORD)
	zipcode = ''
	since = None
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
			# if mentions is blank then this will fail
			pass
		time.sleep(30)
		
		
def getCurrentWeather(woeid):
	data = minidom.parse(urllib2.urlopen(YAHOO_FORECAST_URL % woeid))
	condition = data.getElementsByTagName('yweather:condition')[0]
	text = condition.getAttribute('text')
	temp = condition.getAttribute('temp')
	return text,temp
	
def getWOEID(location):
	data = json.loads(urllib2.urlopen(YAHOO_WOEID_URL % (location,YAHOO_APP_ID)).read())
	try:
		woeid = data['places']['place'][0]['woeid']
	except KeyError:
		woeid = None
	return woeid
	
if __name__ == '__main__':
	main()