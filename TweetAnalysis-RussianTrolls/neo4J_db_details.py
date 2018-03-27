"""
Author: Erin Riglin
"""
import os

class Neo4j_Database:

    def __init__(self):
        self.server = "bolt://XXXX:XXXX"
        self.username = "neo4j"
        self.password = "XXXX"

        self.local_entity_file = "local_db_entities.csv"
        self.local_relation_file = "local_db_relations.csv"
        self.local_import_error_file = "import_relations_errors.csv"

        self.troll_entity_file = "troll_db_entities_utf8.csv"
        self.troll_relation_file = "troll_db_rel_utf8_uniques.csv"
        
        self.query_failure_log_file = "query_failure_log.csv"
        
        self.newyorkers_file = os.path.abspath(os.path.join(os.path.dirname(__file__),  'data', "mentioned_NY-ONLY.csv"))
