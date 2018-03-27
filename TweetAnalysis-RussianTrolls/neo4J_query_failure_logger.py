"""
Author: Erin Riglin
"""
import pandas as pd
import neo4J_db_details
import os.path
import datetime

"""
Class for logging errors
"""

def log(process, message, error):
    
    db = neo4J_db_details.Neo4j_Database()
    header = ['time', 'process', 'message', 'error']
    print("======================== Error ========================\n{0}\n{1}\n{2}\n".format(process, message, error))
    
    try:       
        if not os.path.isfile(db.query_failure_log_file):
            pd.DataFrame([], columns=header).to_csv(db.query_failure_log_file, index=False, encoding='utf-8')
        
        df = pd.read_csv(db.query_failure_log_file, encoding='utf-8')
        df = df.append(pd.DataFrame([[datetime.datetime.now(), process, message, error]], columns=list(df.columns.values)))
        df.to_csv(db.query_failure_log_file, index=False, encoding='utf-8')
    
    except Exception as e:
        print("Could not log error: " + str(e))
        
if __name__ == "__main__":

    log('test1', 'test2', 'test3')
