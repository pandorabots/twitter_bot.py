import tweepy
import re 
import os.path
import time
import argparse
import sys
from pb_py import main as pandorabots_api


host = 'INSERT HOST SERVER HERE'
botname = 'INSERT BOT NAME HERE'
app_id = 'INSERT APPNAME HERE'
user_key = 'INSERT USER KEY HERE'

access_token = 'INSERT ACCESS TOKEN HERE'
access_token_secret = 'INSERT ACCESS TOKEN SECRET HERE'

consumer_key = 'INSERT CONSUMER KEY HERE'
consumer_secret = 'INSERT CONSUMER SECRET HERE'


def tweeter(output,screen_name):
    status_update = output + ' @' + screen_name
    print 'Tweeting back: ' + status_update
    try:
        twitter_api.update_status(status_update)
    except:
        print tweepy.TweepError
        print 'There was an error with your tweet'

def query_bot(text, screen_name, cust_id):
    #remove any '@usernames' from tweet
    user_input = re.sub('@[a-zA-Z0-9_]{1,15}','',text).strip()
    output = pandorabots_api.talk(user_key, app_id, host, botname, user_input, clientID = cust_id)["response"]
    return output
    

def fetch_mentions(last_tweet_id):
    print 'Fetching your mentions.'
    if last_tweet_id:
        mentions = twitter_api.mentions_timeline(since_id=last_tweet_id)
    else:
        mentions = twitter_api.mentions_timeline()
    if not mentions:
        print 'you have no new mentions'
    return mentions
    
def maintain_log(tweet_id, text, screen_name, author, user_id):
    pbots_cust_id = user_id
    tweet_list = [tweet_id, pbots_cust_id, author, user_id, text] 
    # add tweet to the tweet dict
    if screen_name in tweet_dict:
        tweet_dict[screen_name].append(tweet_list)
    else:
        tweet_dict[screen_name] = [tweet_list]
    # add tweet to log
    tweet_log.write(screen_name + ' ' + ' ' .join(tweet_list) + '\n')

    

def check_rate_limit_status():
    rate_limit = twitter_api.rate_limit_status()
    mentions_remaining = rate_limit['resources']['statuses']['/statuses/mentions_timeline']['remaining']
    if mentions_remaining != 0:      
        #fetch_mentions(last_tweet)
        print 'You now have ' + str(mentions_remaining - 1) + ' checks for mentions left'
        return True
    else:
        print 'You have reached your limit for mention checks in this rate limit window. Please wait a few minutes and try again.'
        return False

def setup():
    try:
        tweet_log = open('tweet_log.txt','rb')
    except:
        ofile = open('tweet_log.txt','w')
        ofile.write('screen_name 478595937619542017 pbots_cust_id name user_id text\n')
        ofile.close()
        tweet_log = open('tweet_log.txt','rb')
    tweet_dict = {}
    last_tweet_id = ''
    #verify your credentials with twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #create api handler
    twitter_api = tweepy.API(auth)
    #initialize self
    me = twitter_api.me()
    my_id = me.id
    my_screen_name =  me.screen_name
    for line in tweet_log:
        split_line = line.split()
        screen_name = split_line[0]
        #create dict from log
        if screen_name in tweet_dict:
            tweet_dict[screen_name].append(split_line[1:])
        else:
            tweet_dict[screen_name] = [split_line[1:]]
        tweet_id = split_line[1]
        #get most recent tweet replied to
        if tweet_id > last_tweet_id:
            last_tweet_id = tweet_id
    tweet_log.close()
    tweet_log = open('tweet_log.txt','a')
    return tweet_dict, auth, twitter_api, me, my_id, my_screen_name, tweet_log

def main():
    # open tweet_log for appending
    last_tweet_id = open('tweet_log.txt','rb').readlines()[-1].split()[1]
    tweet_log = open('tweet_log.txt','a')
    if (check_rate_limit_status()):
        mentions = fetch_mentions(last_tweet_id)
        tweet_id_list = []
        main_tweet_dict = {}
        for tweet in mentions:
            is_following = tweet.author.following
            user_id = tweet.author.id
            author = tweet.author.name
            text = tweet.text
            screen_name = tweet.author.screen_name
            main_tweet_dict[tweet.id] = [text,screen_name,author,str(user_id)]
            # follow the tweet author if not already
            if not is_following and not my_id==user_id:
                twitter_api.create_friendship(id=user_id)
                print "you are now following: " + screenname 
            if screen_name != my_screen_name and str(tweet.id) not in tweet_id_list:
                print "User " + author + ' @' + screen_name + ' tweeted: "' + text + '"'
                # get the bot's response to the query
                response = query_bot(text, screen_name, user_id)
                if response:
                    tweeter(response,screen_name)
            tweet_id_list.append(str(tweet.id))
        # make sure entries are added to log in corrrect order
        for key in sorted(main_tweet_dict.keys()):
            value = main_tweet_dict[key]
            maintain_log(str(key), value[0], value[1], value[2], str(value[3]))
    tweet_log.close()

    
tweet_dict, auth, twitter_api, me, my_id, my_screen_name, tweet_log = setup()


def run():
    while True:
        main()
        time.sleep(120)

def Main(argv=None):
  parser = argparse.ArgumentParser(
    description='creates Pandorabots Twitter interface')
  parser.add_argument('--continuous',
                      help='if you want the program to be continuous  set to true',
                      metavar='ID', required=False)
  args = parser.parse_args(argv[1:])
  if args.continuous:
      run()
  else:
      main()

if __name__ == "__main__":
  sys.exit(Main(sys.argv))
