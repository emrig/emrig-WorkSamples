# pip install neo4j-driver

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import neo4J_db_details

"""driver = GraphDatabase.driver(
    "bolt://XX.XX.XX.XX:XXXX", 
    auth=basic_auth("XXXX", "XXXX"))"""

db = neo4J_db_details.Neo4j_Database()

driver = GraphDatabase.driver(
    db.server,
    auth=basic_auth(db.username, db.password))
session = driver.session()

working_file = db.local_relation_file

entity_format = {

    "MENTIONS":['u.user_key', 't.id'],
    "IN_REPLY_TO":['t1.id', 't2.id'],
    "RETWEETED":['t1.id', 't2.id'],
    "HAS_TAG":['t.id', 'h.tag'],
    "POSTED":['u.user_key', 't.id'],
    "POSTED_VIA":['t.id', 's.name'],
    "HAS_LINK":['t.id', 'u.expanded_url']

}


troll_list = []

for relation in entity_format.keys():

    entity1 = entity_format[relation][0]
    entity2 = entity_format[relation][1]

    cypher_query = "MATCH ({0})-[:{1}]->({2}) RETURN {3}, {4}".format(
        entity1.split('.')[0], relation, entity2.split('.')[0],
        entity1, entity2)

    results = session.run(cypher_query,
                          parameters={})

    for record in results:

        entity = {}
        entity[entity1] = record[entity1]
        entity[entity2] = record[entity2]
        troll_list.append([relation, entity])


df = pd.DataFrame(troll_list, columns=['relation', 'entities'])
df = df.astype(str).drop_duplicates()
    
df.to_csv(working_file, index=False, encoding='utf-8')
