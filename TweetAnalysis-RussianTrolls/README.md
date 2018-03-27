# ny_troll_interaction_analysis
An analysis of New Yorkers' interactions with Russian Trolls

## Create Local Graph Database for Development
Author: Erin Riglin

I wrote scripts to pull the Neo4J sandbox of 450 Russian trolls and ~14000 unresolved users and rebuild the database locally so we can perform tweet analysis either on local machine or AWS. 

### Graph Database Schema
New Schema built from that of [Neo4J Sandbox](https://neo4j.com/sandbox-v2/#)

![alt text](https://raw.githubusercontent.com/TowCenter/IT18-SocialNetworks/44170b87cc2faa9eac3ebf80a2adcc6c3a644545/troll_db_schema.png?token=AiD1cxtYHiKP8xoiqTHGvl-sKiboc2_Tks5atSiEwA%3D%3D "Graph Database Schema")


### Scripts

* **db rebuild** folder has all data and scripts to rebuild the database, but this is not necessary as a complete db backup is provided below. 
* **neo4j_resolve_users.py** calls the Twitter API to resolve user information including Location. 
* **neo4j_pop_nyers.py** labels new yorkers per known NY-NJ locations and creates graph relationships.
* **neo4j_query** is a helper class that can update entities and add tweets to the graph database to help any script that does Tweet API discover and analysis

### Creat Database Instance

  1. Install Neo4J:  
      * <https://neo4j.com/download/>
      
  2. Download troll database backup
      * <https://drive.google.com/file/d/1SOVrhJUDuqg1oM_DYt-X3bILYLAnqrwL/view?usp=sharing>
      * **UPDATE** All users resolved via api and 700 New Yorkers labeled
        * <https://drive.google.com/file/d/122qc8ZvuRGTMnx1s3aR3gMzj-Xm6DDMC/view?usp=sharing>
      * **UPDATE 2** All user interactions and tweets included
        * <https://drive.google.com/open?id=1sLGZMWu9JR9jxVh7WxAiD2h7tfPs2afK>
      
  3. In Neo4J
      * Click New > Project > New Graph > Create a Local Graph
      * Set the database name and password (Use password 'Columbia123')
      * Once database is created, ensure it **remains off**
      
  4. Export the .zip *root* folder **graph.db** to:
      * "C:\Users\\<**user**>\\AppData\Roaming\Neo4j Desktop\Application\neo4jDatabases\\<**database**>\\installation-3.3.3\data\databases\"
      * DIfferent location for Linux
      
  5. Start the database then click Manage
      * Open Browser will take you to the query window
      * Details tab contains Bolt Port xxxx
      * Local server details will be:
          * Server bolt://localhost:xxxx
          * Username: 'neo4j'
          * Password 'Columbia123'
