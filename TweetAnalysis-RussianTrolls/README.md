# Troll Tweet Analysis to Find non-Russian Actors
Author: Erin Riglin  
**All Data removed from sample**

An analysis of accounts labeled as Russian Actors working for the IRA by Twitter ([Exhibit B](https://democrats-intelligence.house.gov/uploadedfiles/exhibit_b.pdf)) to find accounts that are legitimate, ordinary citizens who were misidentified and erroneously suspended.

## Analysis Scripts

* **db rebuild** folder has all data and scripts to rebuild the database, but this is not necessary as a complete db backup is provided below. 
* **neo4J-get_tweets.py** Asynchronously (up to 100 processes) retrieves known trolls, real users, hashtags, and links from our database and, using Twarc, retrieves the last 3200  tweets from each user and parses for known troll mentions, replies, hashtags, and links. Tweets added to database and appropriate relationships built.
* **neo4j_query.py** Helper class to store entities and relationships into graph database.
* **neo4j_resolve_user.py** Database provided only contains screen names for users that interacted with trolls. This script resolves those users and populates db entity with full details.
* **neo4j_query_failure_logger** Logging class
* **twitter_credentials** Credential class that randomly selects from n (user input) tokens for API calls assigned to each process to minimize limit restrictions.

## Create Local Graph Database for Development

I wrote scripts to pull the Neo4J sandbox of 450 Russian trolls and ~14000 unresolved users and rebuild the database locally so we can perform tweet analysis either on local machine or AWS. 

### Graph Database Schema
New Schema built from that of [Neo4J Sandbox](https://neo4j.com/sandbox-v2/#)

![image](https://github.com/emrig/emrig-WorkSamples/raw/master/TweetAnalysis-RussianTrolls/troll_db_schema.png "Graph Database Schema")

### Creat Database Instance

  1. Install Neo4J:  
      * <https://neo4j.com/download/>
      
  2. Download troll database backup
      * --removed--
      * **UPDATE** All users resolved via api and 700 New Yorkers labeled
        * --removed--
      * **UPDATE 2** All user interactions and tweets included
        * --removed--
      
  3. In Neo4J
      * Click New > Project > New Graph > Create a Local Graph
      * Set the database name and password (Use password --removed--)
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
          * Password --removed--

