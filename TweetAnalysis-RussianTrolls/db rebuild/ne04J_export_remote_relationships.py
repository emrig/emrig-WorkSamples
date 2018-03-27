# -*- coding: utf-8 -*-
"""
Author Erin RIglin
"""

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import os
from os.path import join
import time

driver = GraphDatabase.driver(
    "bolt://XX.XX.XX.XX:XXXX",
    auth=basic_auth("XXXX", "XXXX"))
session = driver.session()

troll_db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "troll_db_entities_utf8.csv"))
troll_db = pd.DataFrame.from_csv(troll_db_file, encoding='utf-8')
troll_db_output = os.path.abspath(os.path.join(os.path.dirname(__file__), "troll_db_rel_utf8.csv"))
relation_db_exist = os.path.abspath(os.path.join(os.path.dirname(__file__), "troll_db_rel_utf8.csv"))
relation_db_completed_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "troll_db_rel_completed.csv"))

global relation_db_completed
relation_db_completed = pd.read_csv(relation_db_completed_file, encoding='utf-8')

# Create some queries that might be formatted with any id using .format()
queries = {
    'POSTED': "MATCH (u:User)-[:POSTED]->(t:Tweet) WHERE u.user_key = '{0}' RETURN u.user_key, t.id",
    'MENTIONS': "MATCH (t:Tweet)-[:MENTIONS]->(u:User) WHERE u.user_key = '{0}' RETURN u.user_key, t.id",
    'IN_REPLY_TO': "MATCH (t1:Tweet)-[:IN_REPLY_TO]->(t2:Tweet) WHERE t1.id = '{0}' RETURN t1.id, t2.id",
    'RETWEETED': "MATCH (t1:Tweet)-[:RETWEETED]->(t2:Tweet) WHERE t1.id = '{0}' RETURN t1.id, t2.id",
    'POSTED_VIA': "MATCH (t:Tweet)-[:POSTED_VIA]->(s:Source) WHERE s.name = '{0}' RETURN t.id, s.name",
    'HAS_LINK': "MATCH (t:Tweet)-[:HAS_LINK]->(u:URL) WHERE u.expanded_url = '{0}' RETURN t.id, u.expanded_url",
    'HAS_TAG': "MATCH (t:Tweet)-[:HAS_TAG]->(h:Hashtag) WHERE h.tag = '{0}' RETURN t.id, h.tag",
}

queries_to_run = {
    """Performance optimization, avoid iterating through individual tweets"""
    'User': ['POSTED'],
    'Source': ['POSTED_VIA'],
    'URL': ['HAS_LINK']
}

errors = []

def run_query(item_label, item_id):

    query_results = []

    for query_type in queries_to_run[item_label]:

        global relation_db_completed
        relation = [query_type, item_id]

        all_relations = relation_db_completed[relation_db_completed['relation'] == query_type]
        x = all_relations[all_relations['entity'] == item_id]

        if len(x) == 0:

            results = []

            try:
                query = queries[query_type]
                results = session.run(query.format(item_id), parameters={})
                relation_db_completed = relation_db_completed.append(pd.DataFrame([relation], columns=['relation', 'entity']))
                relation_db_completed = relation_db_completed.drop_duplicates()
                relation_db_completed.to_csv(relation_db_completed_file, index=False, encoding='utf-8')
                print(str(count) + ": " + str(query_type) + " " + str(item_label) + " " + str(item_id))
                
            except Exception as e:
                print('========ERROR=========\n' + str(e))
                errors.append([item_label, item_id, e])
                continue

            for result in results:
                print(result)
                entities = {result.keys()[0]:result.values()[0], result.keys()[1]:result.values()[1]}
                query_results.append([query_type, entities])

    #print(item_id + " results: " + str(len(query_results)))
    return query_results

def output_csv(new_list, csv):
    df = pd.read_csv(troll_db_output)
    df = pd.concat([df.astype(str),pd.DataFrame(new_list, columns=['relation', 'entities']).astype(str)]).drop_duplicates().reset_index(drop=True)
    df = df.drop_duplicates()
    df.to_csv(csv, index=False, encoding='utf-8')


troll_fields = [field for field in troll_db]
all_results = []
count = 0

# Iterate through each entity in the troll database
for index, item in troll_db.iterrows():

    labels = item['labels']
    props = eval(item['properties'])

    # Run the neo4j query
    if 'Us' in labels:  # User relations
        results = run_query("User", props['user_key'])
        count += 1

    elif 'Source' in labels:  # Tweet relations
        results = run_query("Source", props['name'])
        count += 1

    elif 'URL' in labels:  # Tweet relations
        results = run_query("URL", props['expanded_url'])
        count += 1
        
    for result in results:
        all_results.append(result)


    """Performance: Output to file ever x times"""
    if count % 100 == 0:
        print(count)
        output_csv(all_results, troll_db_output)
        all_results = []

print("Errors: " + str(len(errors)))
