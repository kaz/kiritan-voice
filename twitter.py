# coding: UTF-8

import re
import tweepy
import encoder
import kiritan
import logging
import threading

from twitter_token import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET

# ツイートを拾ってencoderに投げる
class StreamListener(tweepy.StreamListener):
	def on_status(self, status):
		logging.info("Receive tweet from @%s" % status.user.screen_name)
		text = re.sub(r'https://t.co/\w+', 'URL', "%s\n%s\n%s" % (status.user.name, status.user.screen_name, status.text))
		encoder.enqueue(kiritan.talk(text))
		
# Streamリスナを起動
def __listen():
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	
	stream = tweepy.Stream(auth=auth, listener=StreamListener())
	stream.userstream()
	
def listen():
	threading.Thread(target=__listen).start()
	