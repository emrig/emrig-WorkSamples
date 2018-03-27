"""
Author: Erin Riglin
"""

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import neo4J_db_details
import neo4J_query_failure_logger
import twitter_credentials as cred
from twarc import Twarc

"""
Use this class to add/update relations and entities in db 
"""

class Neo4j_Queries:

    def __init__(self):
        
        db = neo4J_db_details.Neo4j_Database()
        
        self.driver = GraphDatabase.driver(
            db.server,
            auth=basic_auth(db.username, db.password))
        
        self.session = self.driver.session()
       
    def execute_query(self, query):
        
        try:
            return self.session.run(query, parameters={})

        except Exception as e:
            neo4J_query_failure_logger.log('execute_write_query', query, e)
            return None
    
    """ This function can update properties and labels for a user, such as NewYorker """
    """ Pass the (if there is an update) label(s) as a list and twitter object for properties """
    def update_user_from_api(self, user_key, properties, labels=[], noproperties=False):
        
        required_str_properties = ['id_str', 'screen_name', 'location', 'created_at', 'time_zone']
        required_int_properties = ['protected', 'followers_count', 'statuses_count']
        
        query = "MATCH (u:User {{ user_key: '{0}'}}) ".format(user_key)
        
        for label in labels:
            
            query += "SET u:{0} ".format(label)
        
        if not noproperties:
            
            for string in required_str_properties:
            
                if properties[string]:
                    query += "SET u.{0} = '{1}' ".format(string, properties[string].replace("'", '"'))
            
            for integer in required_int_properties:
                
                if properties[integer]:
                    
                    query += "SET u.{0} = {1} ".format(integer, properties[integer])
            
        query += "SET u.processed = True "
        query += "RETURN u"
        
        result = self.execute_query(query)
        
        if result:

            try:
                result = result.single()
                if result:
                    print(result)
                    return result
            except Exception as e:
                neo4J_query_failure_logger.log('update_user_from_api', str(user_key), e)
        
        print("No Return for {0}".format(user_key))
        return None
        
    def update_user_from_tweepy(self, user_key, properties, labels=[], noproperties=False):
        
        required_str_properties = ['id_str', 'screen_name', 'location', 'created_at', 'time_zone']
        required_int_properties = ['protected', 'followers_count', 'statuses_count']
        
        query = "MATCH (u:User {{ user_key: '{0}'}}) ".format(user_key)
        
        for label in labels:
            
            query += "SET u:{0} ".format(label)
        
        if not noproperties:
            
            for string in required_str_properties:
                
                if string == 'created_at':
                    query += "SET u.{0} = '{1}' ".format(string, eval("properties.{0}".format(string)))
                elif eval("properties.{0}".format(string)):
                    query += "SET u.{0} = '{1}' ".format(string, eval("properties.{0}".format(string)).replace("'", '"'))
            
            for integer in required_int_properties:
                
                if eval("properties.{0}".format(integer)):
                    query += "SET u.{0} = {1} ".format(integer, eval("properties.{0}".format(integer)))
            
        query += "SET u.processed = True "
        query += "RETURN u"
        
        result = self.execute_query(query)
        
        if result:

            try:
                result = result.single()
                if result:
                    print(result)
                    return result
            except Exception as e:
                neo4J_query_failure_logger.log('update_user_from_tweepy', str(user_key), e)
        
        print("No Return for {0}".format(user_key))
        return None
    
    def add_tweet(self, t_id, properties, labels="Tweet"):

        """ Add properties without potential special characters first"""

        required_str_properties = ['created_at', 'in_reply_to_status_id_str', 'in_reply_to_screen_name']
        required_int_properties = ['retweet_count', 'favorite_count']
        
        query = "CREATE (t:{0} {{ id: '{1}', ".format(labels, t_id)
        
        for string in required_str_properties:
            
            if properties[string]:
                query += "{0}: '{1}', ".format(string, properties[string].replace("'", '"'))
            
        for integer in required_int_properties:
            
            query += "{0}: {1}, ".format(integer, properties[integer])        
        
        query = query[:-2]        
        query += "}) RETURN t"
        
        result = self.execute_query(query)
        
        if result:
            result = result.single()
            if result:
                print(result)

                """ Now add text of tweet"""
                query = "MATCH (t:Tweet {{ id: '{0}'}}) SET t.text = {{text}} RETURN t".format(t_id)

                try:
                    result = self.session.run(query, {"text": properties['full_text']})

                except Exception as e:
                    neo4J_query_failure_logger.log('add_tweet', str(t_id), e)
                    return None

                if result:
                    result = result.single()
                    if result:
                        print(result)

                return result
        
        print("No Return for {0}".format(t_id))
        return None
    
    """ EX: ('Tweet', 'id', '1212321323', 'MENTIONS', 'User', 'user_key', 'username')"""
    def add_relation(self, e1_type, e1_key, e1_id, relation, e2_type, e2_key, e2_id):
               
        query = "MATCH (n1:{0} {{ {1}: '{2}'}}), ".format(e1_type, e1_key, e1_id)
        query += "(n2:{0} {{ {1}: '{2}'}}) ".format(e2_type, e2_key, e2_id)
        
        query += "MERGE (n1)-[r:{0}]->(n2) RETURN n1.{1}, type(r), n2.{2}".format(relation, e1_key, e2_key)
                
        result = self.execute_query(query)
        
        if result:
            result = result.single()
            if result:
                print(result)
                return result
        
        print("No Return for ({0})-[{1}]->({2})".format(e1_id, relation, e2_id))
        return None
        
    def create_def_constraints(self):
        
        constraints = ["CREATE CONSTRAINT ON ( hashtag:Hashtag ) ASSERT hashtag.tag IS UNIQUE",
                       "CREATE CONSTRAINT ON ( source:Source ) ASSERT source.name IS UNIQUE",
                       "CREATE CONSTRAINT ON ( troll:Troll ) ASSERT troll.user_name IS UNIQUE",
                       "CREATE CONSTRAINT ON ( tweet:Tweet ) ASSERT tweet.id IS UNIQUE",
                       "CREATE CONSTRAINT ON ( url:URL ) ASSERT url.expanded_url IS UNIQUE",
                       "CREATE CONSTRAINT ON ( user:User ) ASSERT user.user_key IS UNIQUE",
                       "CREATE CONSTRAINT ON ( newyorker:NewYorker ) ASSERT newyorker.user_name IS UNIQUE",
                       "CREATE CONSTRAINT ON ( nylocation:NYLocation ) ASSERT nylocation.location IS UNIQUE"] 
        results = []
        
        for constraint in constraints:
            
            results += self.execute_query(constraint)

        return
    
if __name__ == "__main__":
    
    """ TESTING """
    
    test = Neo4j_Queries()
    test.create_def_constraints()
    t = Twarc(cred.consumer_key, cred.consumer_secret, cred.access_token, cred.access_token_secret)
    

    users = t.user_lookup('cnn')
    
    for user in users:
        test.update_user_from_api('Test', user, ['NewYorker'], noproperties=True)
        break
    
    tweets = t.filter(track='trump')
    
    for tweet in tweets:
        test.add_tweet('TestTWEET', tweet)
        break
    
    test.add_relation('Tweet', 'id', 'TestTWEET', 'MENTIONS', 'User', 'user_key', 'Test')
