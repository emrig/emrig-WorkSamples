# -*- coding: utf-8 -*-
"""
Author Erin Riglin
"""

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import os
import neo4J_db_details

"""
This script can export certain relation types quickly (small amount). See neo4J_export_remote_relationships for larger relationship sets
"""

db = neo4J_db_details.Neo4j_Database()

driver = GraphDatabase.driver(
    "bolt://XX.XX.XX.XX:XXXX",
    auth=basic_auth("XXXX", "XXXX"))
session = driver.session()

troll_db = pd.DataFrame.from_csv(db.troll_entity_file, encoding='utf-8')
troll_db_output = db.troll_relation_file

# Create some queries that might be formatted with any id using .format()
queries = {
    'POSTED': "MATCH (u:User)-[:POSTED]->(t:Tweet) RETURN u.user_key, t.id",
    'MENTIONS': "MATCH (t:Tweet)-[:MENTIONS]->(u:User) RETURN u.user_key, t.id",

    'IN_REPLY_TO': "MATCH (t1:Tweet)-[:IN_REPLY_TO]->(t2:Tweet) RETURN t1.id, t2.id",
    'RETWEETED': "MATCH (t1:Tweet)-[:RETWEETED]->(t2:Tweet) RETURN t1.id, t2.id",
    'POSTED_VIA': "MATCH (t:Tweet)-[:POSTED_VIA]->(s:Source) RETURN t.id, s.name",
    'HAS_LINK': "MATCH (t:Tweet)-[:HAS_LINK]->(u:URL) RETURN t.id, u.expanded_url",
    'HAS_TAG': "MATCH (t:Tweet)-[:HAS_TAG]->(h:Hashtag) RETURN t.id, h.tag",
}

errors = []

def run_query(query_type, query):

    query_results = []

    try:
        query = queries[query_type]
        results = session.run(query, parameters={})
    except Exception as e:
        print('========ERROR=========\n' + str(e))
        errors.append([query_type, query, e])
        return
        
    for result in results:
        #print(result)
        entities = {result.keys()[0]:result.values()[0], result.keys()[1]:result.values()[1]}
        query_results.append([query_type, entities])

    return query_results

def output_csv(new_list, csv):
    df = pd.read_csv(troll_db_output)
    df = df.append(pd.DataFrame(new_list, columns=['relation', 'entities']))
    df = df.drop_duplicates()
    df.to_csv(csv, index=False, encoding='utf-8')


troll_fields = [field for field in troll_db]
all_results = []

# Iterate through each entity in the troll database
for relation in queries.keys():
    
    print(relation)
    results = run_query(relation, queries[relation])
    
    for result in results:
        all_results.append(result)

    output_csv(all_results, troll_db_output)
    all_results = []



print("Errors: " + str(len(errors)))
