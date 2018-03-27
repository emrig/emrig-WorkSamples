# -*- coding: utf-8 -*-
"""
Authors:
Erin Riglin
Alex Calderwood
Shreya Vaidyanathan
"""

import pandas as pd
import twitter_credentials
from twarc import Twarc
import requests
from neo4j_query import Neo4j_Queries
import multiprocessing as mp

"""
This script queries the graph database to get lists of troll accounts, 
accounts that have interacted with troll accounts, hashtags used by trolls,
and links used be trolls.  

Twarc used to retrieve last 3200 tweets of each user and compare known entities.
Any matching entity is added to the graph database with appropriate relationships.

The new entities and relationships will give us users who have interacted with troll accounts,
potential sources

Asynchronous multithreading enabled to break lists down into 100 sub-lists and process in parallel. 
"""

# OVERRIDE Query db for New Yorkers, convert all to lowercase for proper comparison
q = Neo4j_Queries()

# OVERRIDE Previously NY users, but scoped expanded to all non-troll users
global mentioned_users_ny
mentioned_users_ny_list = [x.lower() for x in q.execute_query(
    "MATCH (n:User) WHERE NOT n:Troll RETURN collect(n.user_key) AS result").single()['result']]
mentioned_users_ny = pd.DataFrame(mentioned_users_ny_list, columns=['user_key'])


# OVERRIDE: Query db for Trolls, convert all to lowercase for proper comparison
global trolls_screen_names
trolls_screen_names = [x.lower() for x in
                       q.execute_query("MATCH (t:Troll) RETURN collect(t.screen_name) AS result").single()['result']]

# Read in the hashtags used by trolls, convert all to lowercase for proper comparison
global troll_hashtags
troll_hashtags = [x.lower() for x in
                  q.execute_query("MATCH (h:Hashtag) RETURN collect(h.tag) AS result").single()['result']]

# Read in the links used by trolls
global troll_urls
troll_urls = q.execute_query("MATCH (u:URL) RETURN collect(u.expanded_url) AS result").single()['result']

# Set search scope
global check_replies
global check_mentions
global check_hashtags
global check_urls

check_replies = True
check_mentions = True
check_hashtags = False
check_urls = False

def get_interaction_tweets(user_screen_name):

    global trolls_screen_names
    global troll_hashtags
    global troll_urls

    matched_replies = []
    matched_mentions = []
    matched_hashtags = []
    matched_urls = []

    # twitter_credentials class randomly selects 1 of 3 available API keys
    cred = twitter_credentials.twitter_credentials()

    # Create a Twarc object
    t = Twarc(cred.consumer_key, cred.consumer_secret, cred.access_token, cred.access_token_secret)

    result = t.timeline(screen_name=user_screen_name, since_id='2015-01-01')

    for tweet in result:

        # Confirm the tweet result is for the right user
        if not tweet['user']['screen_name'].lower() == user_screen_name:
            continue

        # Determine if each tweet in result was in reply to one of the trolls
        if tweet['in_reply_to_screen_name']:

            screen_name = tweet['in_reply_to_screen_name'].lower()

            if screen_name in trolls_screen_names:
                matched_replies.append((tweet, screen_name))

        entities = tweet['entities']

        # Determine if each tweet in result has mentioned one of the trolls
        if entities:

            user_mentions = entities['user_mentions']
            hashtags = entities['hashtags']
            urls = entities['urls']

            if user_mentions:

                for user_mention in user_mentions:

                    screen_name = user_mention['screen_name'].lower()

                    if screen_name in trolls_screen_names:
                        matched_mentions.append((tweet, screen_name))

            # Determine if each tweet in result uses a hashtag known to be used by trolls
            if hashtags:

                for hashtag in hashtags:

                    tag = hashtag['text'].lower()

                    if tag in troll_hashtags:
                        matched_hashtags.append((tweet, tag))

            # Determine if each tweet in result uses a url known to be used by trolls
            if urls:

                for url in urls:

                    expanded_url = url['expanded_url']

                    if expanded_url in troll_urls:
                        matched_urls.append((tweet, expanded_url))

    return matched_replies, matched_mentions, matched_hashtags, matched_urls

def write_tweets_to_db(mentioned_users_ny, process):

    # Include scope
    global check_replies
    global check_mentions
    global check_hashtags
    global check_urls

    # Initialize the querying object
    q = Neo4j_Queries()
    q.create_def_constraints()

    # Write to Mentions / Replies CSV
    mentions_csv = pd.DataFrame([], columns=['user_screen_name', 'interaction_type', 'tweet_id', 'mentioned_or_replied_to'])
    replies_csv = pd.DataFrame([], columns=['user_screen_name', 'interaction_type', 'tweet_id', 'mentioned_or_replied_to'])
    hashtags_csv = pd.DataFrame([], columns=['tweet_id', 'interaction_type', 'tag', 'user_screen_name'])
    urls_csv = pd.DataFrame([], columns=['tweet_id', 'interaction_type', 'url', 'user_screen_name'])

    count = 0

    for index, user in mentioned_users_ny.iterrows():

        count += 1
        u_screen_name = user['user_key']

        print("{0}-[{1}] Searching user: {2}".format(process, str(str(count) + ":" + str(len(mentioned_users_ny))), u_screen_name))

        try:
            t_replies, t_mentions, t_hashtags, t_urls = get_interaction_tweets(u_screen_name)

            if check_replies:
                for match in t_replies:

                    tweet, t_screen_name = match
                    # Write to the CSV
                    replies_csv = replies_csv.append(pd.DataFrame([[u_screen_name, 'reply', tweet['id'], t_screen_name]], columns=list(replies_csv.columns.values)))
                    replies_csv.to_csv('data/{0}-replies_all.csv'.format(process), index=False, encoding='utf-8')

                    # Create the Tweet in the db
                    q.add_tweet(tweet['id'], tweet)
                    # Create the relation in the db
                    q.add_relation('User', 'user_key', u_screen_name, 'POSTED', 'Tweet', 'id', tweet['id'])

                    """ Some Troll tweets may not be in database, will have to add manually for now"""
                    q.add_relation('Tweet', 'id', tweet['id'], 'IN_REPLY_TO', 'Tweet', 'id', tweet['in_reply_to_status_id'])

            if check_mentions:
                for tweet, t_screen_name in t_mentions:
                    mentions_csv = mentions_csv.append(pd.DataFrame([[u_screen_name, 'mention', tweet['id'], t_screen_name]], columns=list(mentions_csv.columns.values)))
                    mentions_csv.to_csv('data/{0}-mentions_all.csv'.format(process), index=False, encoding='utf-8')

                    # Create the Tweet in the db
                    q.add_tweet(tweet['id'], tweet)
                    # Create the relations in the db
                    q.add_relation('User', 'user_key', u_screen_name, 'POSTED', 'Tweet', 'id', tweet['id'])
                    q.add_relation('Tweet', 'id', tweet['id'], 'MENTIONS', 'Troll', 'user_key', t_screen_name)

            if check_hashtags:
                for tweet, tag in t_hashtags:
                    hashtags_csv = hashtags_csv.append(pd.DataFrame([[tweet['id'], 'has_tag', tag, u_screen_name]], columns=list(hashtags_csv.columns.values)))
                    hashtags_csv.to_csv('data/hashtags2.csv', index=False, encoding='utf-8')
                    # Create the Tweet in the db
                    q.add_tweet(tweet['id'], tweet)
                    # Create the relations in the db
                    q.add_relation('User', 'user_key', u_screen_name, 'POSTED', 'Tweet', 'id', tweet['id'])
                    q.add_relation('Tweet', 'id', tweet['id'], 'HAS_TAG', 'Hashtag', 'tag', tag)

            if check_urls:
                for tweet, expanded_url in t_urls:
                    urls_csv = urls_csv.append(pd.DataFrame([[tweet['id'], 'has_link', expanded_url, u_screen_name]], columns=list(urls_csv.columns.values)))
                    urls_csv.to_csv('data/urls2.csv', index=False, encoding='utf-8')
                    # Create the Tweet in the db
                    q.add_tweet(tweet['id'], tweet)
                    # Create the relations in the db
                    q.add_relation('User', 'user_key', u_screen_name, 'POSTED', 'Tweet', 'id', tweet['id'])
                    q.add_relation('Tweet', 'id', tweet['id'], 'HAS_LINK', 'URL', 'expanded_url', expanded_url)

        except requests.exceptions.HTTPError:
            print("Error with user {}. Might be a private user idk...".format(u_screen_name))
        continue



if __name__ == "__main__":
    # Multithreading
    nprocesses = 100

    nentries = len(mentioned_users_ny)
    print(nentries)
    list_size = int(nentries / nprocesses)
    pointer = 0
    processes = []
    count = 0

    # Multithreading enabled to break list of users into segments and process in parallel
    while pointer < nentries:
        processes.append(mp.Process(target=write_tweets_to_db, args=(mentioned_users_ny[pointer:pointer + list_size], "{0}-{1}".format(pointer, pointer + list_size))))
        count += 1
        pointer += list_size

    for p in processes:
        p.start()
