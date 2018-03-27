# -*- coding: utf-8 -*-
"""
Author Erin Riglin
"""

"""
Database provided only contains screen names for users that interacted with trolls. 
This script resolves those users and populates db entity with full details.
"""

import twitter_credentials as cred
import tweepy
import datetime
import time
import neo4j_query

auth = tweepy.OAuthHandler(cred.consumer_key, cred.consumer_secret)

reverse = True

auth.set_access_token(cred.access_token, cred.access_token_secret)
api = tweepy.API(auth)

if reverse:
    query = "MATCH (u:User) where u.processed IS NULL return u ORDER BY u.user_key DESC"

else:
    query = "MATCH (u:User) where u.processed IS NULL return u ORDER BY u.user_key ASC"
    
search = neo4j_query.Neo4j_Queries()
results = search.execute_query(query)

for result in results:

    if 'Troll' not in result['u'].labels:
        
        user = result['u'].properties['user_key']
        
        try:
            queries_remaining = api.rate_limit_status()['resources']['users']['/users/search']['remaining']
            api_result = api.search_users(user)
            
        except tweepy.TweepError as e:
            print(e)
            
            if eval(str(e))[0]['code'] == 88: 
                print("Limit Reached. Retry in 5 min. " + str(datetime.datetime.now()))
                time.sleep(5*60)
                continue
            else: 
                continue
        
        found = False
        
        for obj in api_result:
            if obj.screen_name.lower() == user.lower():
                found = True
                break
            
        if not found:
            search.update_user_from_api(user, [], noproperties=True)
        
        else:
            search.update_user_from_tweepy(user, obj)
