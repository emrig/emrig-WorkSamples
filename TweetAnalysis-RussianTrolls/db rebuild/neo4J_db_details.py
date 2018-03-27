"""
Author: Erin Riglin
"""

class Neo4j_Database:

    def __init__(self):
        self.server = "bolt://XX.XX.XX.XX:XXXX"
        self.username = "XXXX"
        self.password = "XXXX"

        self.local_entity_file = "local_db_entities.csv"
        self.local_relation_file = "local_db_relations.csv"
        self.local_import_error_file = "import_relations_errors.csv"

        self.troll_entity_file = "troll_db_entities_utf8.csv"
        self.troll_relation_file = "troll_db_rel_utf8_uniques.csv"
