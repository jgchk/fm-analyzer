# What It Does
This program goes through every song you've ever scrobbled to last.fm and checks if it comes from an album that's on Spotify. If it is, it keeps track of the data in order to calculate the following averages for your Spotify listening habits:
* **artist streams**: average number of times you stream tracks by an artist
* **album streams**: average number of times you stream an album
* **album length**: average number of tracks of the albums you have listened to
* **payouts**: theoretical per-album and per-track payouts of every major music streaming platform based on your music listening habits, calculated by multiplying their per track payouts by album streams then dividing by album length. If you listen to an album all the way through more than once on average (album streams > album length), the calculated values will end up higher than the actual per-stream payouts of these companies.

# How To Run
1. Install requirements with `pip install -r requirements.txt`
1. Run `python main.py <last.fm username> <last.fm password> <spotify username>` with Python 3
1. You will need to finish authentication with Spotify through your web browser. Click the auth link when prompted by the program.
1. Wait for a while. Last.fm takes forever to retrieve your entire listening history, especially if you have a lot of scrobbles.
1. Once your listening history is retrieved, you will see album names begin to be printed out. Each one is an album from your listening history that was found on Spotify.
1. After analyzing your entire history, your statistics will be printed out. Below is an example:
![alt text](https://i.imgur.com/tJgZK32.png "Streaming Info")
