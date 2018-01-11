
import os.path
import tweepy
import csv
import sys
import os
from tweepy import OAuthHandler
import json
import wget
import argparse
import configparser

consumer_key = "ujQqHysqSd8uByZZV0bQ4CPLN"
consumer_secret = "hoLl4A0nLYM647HrOJ3dlvlm6rmAbxCkO7tprGXfWTJlwyqzYk"
access_token = "896414629231960064-BOx97WFk1pXjNsm16vQbcro3HMlFZma"
access_secret = "v74WlYKOkYkvxw2nZg52tkK31PdU2PGsoW9Lwm9vI8PXa"

#TODO: Limit by number of tweets?
def parse_arguments():
  parser = argparse.ArgumentParser(description='Download pictures from a Twitter feed.')
  parser.add_argument('username', type=str, help='The twitter screen name from the account we want to retrieve all the pictures')
  parser.add_argument('--num', type=int, default=10, help='Maximum number of tweets to be returned.')
  parser.add_argument('--retweets', default=False, action='store_true', help='Include retweets')
  parser.add_argument('--replies', default=False, action='store_true', help='Include replies')
  #parser.add_argument('--output', default='../'+username+'/', type=str, help='folder where the pictures will be stored')

  args = parser.parse_args()
  return args

def parse_config(config_file):
  config = configparser.ConfigParser()
  config.read(config_file)  
  return config 
  
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status

def init_tweepy():
  # Status() is the data model for a tweet
  tweepy.models.Status.first_parse = tweepy.models.Status.parse
  tweepy.models.Status.parse = parse
  # User() is the data model for a user profil
  tweepy.models.User.first_parse = tweepy.models.User.parse
  tweepy.models.User.parse = parse

def authorise_twitter_api():
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_secret)
  return auth

def download_images(api, username, retweets, replies, num_tweets, output_folder):
  tweets = api.user_timeline(screen_name=username, count=10, include_rts=retweets, exclude_replies=replies)
  if not os.path.exists(output_folder):
      os.makedirs(output_folder)

  downloaded = 0
  while (len(tweets) != 0):    
    last_id = tweets[-1].id
    
    for status in tweets:
      media = status.entities.get('media', []) 
      if(len(media) > 0 and downloaded < num_tweets):
        wget.download(media[0]['media_url'], out=output_folder)
        downloaded += 1        

    tweets = api.user_timeline(screen_name=username, count=10, include_rts=retweets, exclude_replies=replies, max_id=last_id-1)

def main():    
  arguments = parse_arguments() 
  username = arguments.username
  retweets = arguments.retweets
  replies = arguments.replies
  num_tweets = arguments.num
  #output_folder = arguments.output
  output_folder=os.path.join('D:\proj\Twitter-Image-Downloader-master',username)
  #config = parse_config('../config.cfg')
  auth = authorise_twitter_api()   
  api = tweepy.API(auth)
  number_of_tweets = 10

	#get tweets
  tweets = api.user_timeline(screen_name = username,count = number_of_tweets)

	#create array of tweet information: username, tweet id, date/time, text
  tweets_for_csv = [[username,tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in tweets]

	#write to a new csv file from the array of tweets
  print "writing to {0}_tweets.csv".format(username)
  with open("{0}_tweets.csv".format(username) , 'w+') as file:
	writer = csv.writer(file, delimiter='|')
	writer.writerows(tweets_for_csv)


  download_images(api, username, retweets, replies, num_tweets, output_folder)

if __name__=='__main__':
    main()
