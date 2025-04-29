# Statistarr
Just a simple python script to keep track of failed and successful grabs per indexer basis. Works only with sonarr and radarr.

### Why?
Prowlarr doesn't track failed grabs. Additionally it creates a json dump of stats, as stats related to deleted Movies/Shows from Radarr/Sonarr go poof as well. 
>[!NOTE]
>Which is to say, initially collected stats will most likely inaccurate. But use it long enough and you get a better idea of how each indexer in your stack fares for movies and tv shows

### How does it work?
It's a stupid script mostly created by gpt. Basically calls v3/history API, filters thru events, notes latest event date, dumps a json with collected stats (picks up json dumps as well, so older stats remain untouched). First completion may take a while depending on history size. I can't vouch for bugs and errors tbh, feel free to open issue. 

### How to use?
Requirements:
* python3 (i used 3.13.3 - was working for me)
* pip
* Install requirements from requirements.txt


I am still figuring out exe file and how to schedule a py or exe file (I am a windows user). I will upload mainly the py files in question and let other users (if this repo even attracts attention) deal with how to schedule it. 

The py scripts (mostly built with windows in mind, open issue if any error) are as follows
* statistarr.py - when run in console, prints a nice output in terminal. Main function being though json dump.
* cchart.py - uses quickchart.io to display the stats in a pretty graph/chart

