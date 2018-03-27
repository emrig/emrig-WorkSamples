# Spotify Artists Crawler

This is a small piece of a larger app we are working on that recommends music based on specific tempo, time signature, and key,
but also allows the user to search for songs on Spotify to find similar music based on the aforementioned properties and Spotify-specific 
qualities such as liveliness, danceability, acousticness, valence, etc.

Overview of Spotify Audio Features [found here](https://developer.spotify.com/web-api/get-audio-features/)

Since the Spotify API does not allow you to query music based on audio features, we have to build our own database that stores all of this 
information for millions of songs.

For discovery, we instantiate a database with 350 known artists across various genres and use the get_related_artists Spotify API to crawl
catalogue.

## Files and Scripts
### artist_crawler.py
This class instantiates a Google Firestorm Database implemented as a FIFO queue with 350 known artists across many genres.
 
We call the Spotify API to get all related artists of a particular artist in the queue.  
If the artists does not already exists, they are added to the queue.

When an artists has been processed, they are stamped with a 'get-related-time' timestamp. 

Artists are filtered by an region or genre defined in the configuration.

Additional scripts in development to get music from each of these users, as well
as the audio features of each track to be stored in our db.

We anticipate 1,000,000+ song audio features to be initially stored in our db.

### sp_search.py
Spotipy library wrapper to fit our needs

### app.json
Configuration file

### initArtist.json
Initial list of known artists

### tests folder
Sample Unittests
