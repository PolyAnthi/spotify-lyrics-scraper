# Spotify Lyrics Grabber
This Spotify Lyrics Grabber is a tool to grab Spotify Lyrics of any song, not just the one you are listening to.

**Table of Contents**

- [Installation](#installation)
- [Examples](#examples)
- [Obtaining sp_key and sp_dc](#obtaining)

### Installation
To install, run `pip install spotify-lyrics-scraper` in your command prompt. To import it, I recommend `import spotify_lyrics_scraper as spotify`

### Obtaining
To obtain the sp_dc or sp_key:
- Open a ***new Incognito Window*** in your browser. Head to https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F
- Open Developer Tools (CTRL+SHIFT+I or F12) and head to the "Network" tab and make sure it is recording.
- Login to Spotify.
- Search/Filter for `?flow_id` in the "Network" tab.
- Under cookies for the request, you will see "sp_dc" and "sp_key".
- Close the window ***WITHOUT LOGGING OUT*** (else said cookies will be made invalid).

### Examples
- Always using: `import spotify_lyrics_scraper as spotify`
- To obtain the sp_dc, please check out https://github.com/akashrchandran/syrics/wiki/Finding-sp_dc. This is required to have access to the lyrics API.
##### Example 1
```
token = spotify.getToken("SP_DC Here")
print(spotify.getLyrics(token, songName="Song"))
```

##### Example 2 (Proxies)
```
token = spotify.getToken("SP_DC Here")
print(spotify.getLyrics(token, songName="Song", proxies={"https": "https://1.1.1.1:443"}))
```

##### Example 3 (Formatting)
```
token = spotify.getToken("SP_DC Here")
lyrics = spotify.getLyrics(token, songName="Song")
if type(lyrics) == spotify.spotifyDict: print(lyrics.formatLyrics()) # there are several modes, 0/none is just lyrics, 1 is starting time in ms, 2 is starting time in seconds
else: print(f"Error: {lyrics}")
```

##### Example 4 (sp_key)
```
token = spotify.getToken("SP_DC Here", "SP_Key Here") #SP Key can give you up to a year worth of spotify tokens.
print(spotify.getLyrics(token, songName="Song"))
```