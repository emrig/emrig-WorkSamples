"""
Author: Erin Riglin
"""
"""
Can be improved with multiprocessing. See neo4j_import_relations_multithread.py
"""

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import neo4J_export_entities
import neo4J_db_details

""" DONT FORGET TO CREATE CONSTRAINTS FIRST """
"""
"CONSTRAINT ON ( hashtag:Hashtag ) ASSERT hashtag.tag IS UNIQUE"
"CONSTRAINT ON ( source:Source ) ASSERT source.name IS UNIQUE"
"CONSTRAINT ON ( troll:Troll ) ASSERT troll.user_name IS UNIQUE"
"CONSTRAINT ON ( tweet:Tweet ) ASSERT tweet.id IS UNIQUE"
"CONSTRAINT ON ( url:URL ) ASSERT url.expanded_url IS UNIQUE"
"CONSTRAINT ON ( user:User ) ASSERT user.user_key IS UNIQUE"
"""

db = neo4J_db_details.Neo4j_Database()

driver = GraphDatabase.driver(
    db.server,
    auth=basic_auth(db.username, db.password))
session = driver.session()

"""Get Troll DB entities"""
db_entities = pd.read_csv(db.troll_entity_file, encoding='utf-8')

"""Get existing entities in local db to save time"""
neo4J_export_entities.export_to_csv(db.server, db.username, db.password, db.local_entity_file)
db_existing_entities = pd.read_csv(db.local_entity_file, encoding='utf-8')

"""All possible properties by data type for query builder"""
string_properties = ['created_str', 'created_at', 'description', 'user_key', 'time_zone', 'screen_name', 'name', 'location', 'lang', 
                     'id', 'expanded_url', 'tag', 'text', ]

int_properties = ['retweet_count', 'retweeted', 'friends_count', 'listed_count', 'favourites_count', 'verified', 'statuses_count','followers_count']

def query_builder(label, actual_properties):
    
    query = 'CREATE (n:{0} {{ '.format(label)

    for prop in string_properties:

        if prop in actual_properties.keys():
            substring = str(actual_properties[prop]).replace('"', '\'')
            query += "{0}: \"{1}\",".format(prop, substring)

    for prop in int_properties:
        if prop in actual_properties.keys():
            query += "{0}: {1},".format(prop, actual_properties[prop])

    query = query[:-1]
    query += '}) RETURN n'

    return query

errors = []
    
for index, item in db_entities.iterrows():
    
    label = item[1]
    properties = eval(item[2])
    query = ""
    
    x = db_existing_entities[db_existing_entities['properties'].str.contains(properties['id'])]
    
    if len(x) == 0: 
    
        if label == "{'User', 'Troll'}":
            query = query_builder("User:Troll", properties)
        elif label == "{'Tweet'}":
            query = query_builder("Tweet", properties)
        elif label == "{'User'}":
            query = query_builder("User", properties)
        elif label == "{'Hashtag'}":
            query = query_builder("Hashtag", properties)
        elif label == "{'URL'}":
            query = query_builder("URL", properties) 
        elif label == "{'Source'}":
            query = query_builder("Source", properties)
            
        if query:
            
            try:
                results = session.run(query, parameters={})
                for result in results:
                    print(result)
            except Exception as e:
                print(e)
                errors.append([label,properties])
            
print("Errors: " + str(len(errors)))
