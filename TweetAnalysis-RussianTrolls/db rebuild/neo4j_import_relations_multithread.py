"""
Author: Erin Riglin
"""

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import random
import multiprocessing as mp
import neo4J_db_details

"""
Since there 490,000 relationships and each takes ~1 sec to write,
Adding start points to run scripts in parallel to cover each 'nprocesses' size of the list.

This program slices the input list into n size chunks and process them in parallel
"""

"""Number of slices and which direction to iterate"""
nprocesses = 100
reverse = False

"""Initialize Bolt connect with DB"""
db = neo4J_db_details.Neo4j_Database()

driver = GraphDatabase.driver(
    db.server,
    auth=basic_auth(db.username, db.password))
session = driver.session()

"""Read export relationships from Sandbox"""
troll_db_relations = pd.read_csv('troll_db_rel_utf8_uniques.csv', encoding='utf-8')

""" USE FOR SPECIFIC RELATIONS"""
troll_db_relations = troll_db_relations[troll_db_relations['relation'] == 'MENTIONS']

troll_db_relations = troll_db_relations.values.tolist()

global errors 
errors = pd.read_csv('import_relations_errors.csv', encoding='utf-8')
global count
count = 0

"""Relationships already in the DB"""
existing_db_relations = pd.read_csv('local_db_relations.csv', encoding='utf-8')

"""Relation types to skip to """
relations_to_skip = ['POSTED_VIA']

queries = {
        'MENTIONS':"MATCH (u:User {{ user_key: '{0}' }}),(t:Tweet {{ id: '{1}' }}) USING INDEX u:User(user_key) USING INDEX t:Tweet(id) MERGE (t)-[m:MENTIONS]->(u) RETURN t.id, type(m), u.user_key",
        'POSTED':"MATCH (u:User {{ user_key: '{0}' }}),(t:Tweet {{ id: '{1}' }})  USING INDEX u:User(user_key) USING INDEX t:Tweet(id) MERGE (u)-[p:POSTED]->(t) RETURN t.id, type(p), u.user_key",
        'HAS_TAG':"MATCH (t:Tweet {{ id: '{0}' }}),(h:Hashtag {{ tag: '{1}' }}) USING INDEX h:Hashtag(tag) USING INDEX t:Tweet(id) MERGE (t)-[h1:HAS_TAG]->(h) RETURN t.id, type(h1), h.tag",
        'RETWEETED':"MATCH (t1:Tweet {{ id: '{0}' }}),(t2:Tweet {{ id: '{1}' }}) USING INDEX t1:Tweet(id) USING INDEX t2:Tweet(id) MERGE (t1)-[r:RETWEETED]->(t2) RETURN t1.id, type(r), t2.id",
        'IN_REPLY_TO':"MATCH (t1:Tweet {{ id: '{0}' }}),(t2:Tweet {{ id: '{1}' }}) USING INDEX t1:Tweet(id) USING INDEX t2:Tweet(id) MERGE (t1)-[i:IN_REPLY_TO]->(t2) RETURN t1.id, type(i), t2.id",
        'POSTED_VIA':"MATCH (t:Tweet {{ id: '{0}' }}),(s:Source {{ name: '{1}' }}) USING INDEX s:Source(name) USING INDEX t:Tweet(id) MERGE (t)-[p:POSTED_VIA]->(s) RETURN t.id, type(p), s.name",
        'HAS_LINK':"MATCH (t:Tweet {{ id: '{0}' }}),(u:URL {{ expanded_url: '{1}' }}) USING INDEX u:URL(expanded_url) USING INDEX t:Tweet(id) MERGE (t)-[h:HAS_LINK]->(u) RETURN t.id, type(h), u.expanded_url"
        }

def run_query(process, remaining,  relation, entity1, entity2):

    global errors

    header = "[{0}][{1}]".format(process, remaining)
    try:
        result = session.run(queries[relation].format(entity1, entity2), parameters={})
        result = result.single()
        
        if result:
            print("{0} {1}".format(header, result))
            return
            
        else:
            raise ValueError('Relation not created {0}-{1}-{2}'.format(relation, entity1, entity2))
        
    except Exception as e:
        print('========ERROR=========\n' + str(header) + " " + str(relation) +','+ str(entity1) +','+ str(entity2) +','+ str(e))
        errors = errors.append(pd.DataFrame([[relation, entity1, entity2, str(e)]], columns=['relation', 'entity1', 'entity2', 'error']))
        errors.to_csv('import_relations_errors.csv', index=False, encoding='utf-8')

    return

def import_list(relation_list, process):

    list_size = len(relation_list)
    count = 0

    if reverse:
        relation_list.reverse()
        process = "{0}-{1}".format(process.split('-')[1], process.split('-')[0])

    for relation, entities in relation_list:

        remaining = list_size - count
        header = "[{0}][{1}]".format(process, remaining)

        if not ((existing_db_relations['relation'] == str(relation)) & (existing_db_relations['entities'] == str(entities))).any() and relation not in relations_to_skip:

            entities = list(eval(entities).values())
            run_query(process, remaining, relation, entities[0], entities[1])

        else:
            print(str(header) + " Exists: " + str(relation) + " " + str(entities))

        count += 1

def threads(number):

    nentries = len(troll_db_relations)
    list_size = int(nentries / number)
    pointer = 0
    processes = []
    count = 0


    while pointer < nentries:
        processes.append(mp.Process(target=import_list, args=(troll_db_relations[pointer:pointer+list_size], "{0}-{1}".format(pointer, pointer+list_size))))
        count += 1
        pointer += list_size

    for p in processes:
        p.start()



if __name__ == "__main__":

    threads(nprocesses)
