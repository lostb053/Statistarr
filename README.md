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
* Install requirements
```
pip install requests quickchart.io
```


I am still figuring out exe file and how to schedule a py or exe file (I am a windows user). I will upload mainly the py files in question and let other users (if this repo even attracts attention) deal with how to schedule it. 

The py scripts (mostly built with windows in mind, open issue if any error) are as follows
* statistarr.py - when run in console, prints a nice output in terminal. Main function being though json dump.
* cchart.py - uses quickchart.io to display the stats in a pretty graph/chart

### Screenshots

statistarr.py print output (sorry for the sloppy attempt at hiding indexers 😭)

![Screenshot 2025-04-29 055201](https://github.com/user-attachments/assets/20787e55-4e36-4f30-9b6e-9a2707eee41c)
![Screenshot 2025-04-29 055217](https://github.com/user-attachments/assets/add7f0a2-8306-46a9-ab87-429042c48144)


>[!NOTE]
>Failure rate is calculated by failed grabs / total grabs (success+fail)

cchart.py output

![sf-a6c85628-6cb1-4ceb-b434-20cf053ef10e](https://github.com/user-attachments/assets/a7824839-d075-46d2-beeb-77f8687d7a37)

## Credits
* ChatGPT
* @typpo for [quickchart-python](https://github.com/typpo/quickchart-python)

## The code is bad?
Thank you. I am not a programmer, just a random biology guy
