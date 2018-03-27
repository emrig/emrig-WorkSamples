"""
Author: Erin Riglin
"""

# pip install neo4j-driver

from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd
import neo4J_db_details

"""This script export all entities from a local or remote graph db"""

def export_to_csv(db_address, username, password, file):
    driver = GraphDatabase.driver(
        db_address, 
        auth=basic_auth(username, password))
    session = driver.session()
    
    cypher_query = "MATCH (n) RETURN n"
    
    results = session.run(cypher_query,
      parameters={})
    
    troll_db = {}
    
    for record in results:
        
        entity = {}
        print(record)
        entity['labels'] = record['n'].labels
        entity['properties'] = record['n'].properties
        troll_db[record['n'].id] = entity
       
    troll_list = []
    for entity in troll_db.keys():
        troll_list.append([entity, troll_db[entity]['labels'], troll_db[entity]['properties']])
    
    
    
    df = pd.DataFrame(troll_list, columns=['id', 'labels', 'properties'])
        
    df.to_csv(file, index=False, encoding='utf-8')

if __name__ == "__main__":

    db = neo4J_db_details.Neo4j_Database()
    export_to_csv(db.server, db.username, db.password, db.local_entity_file)
