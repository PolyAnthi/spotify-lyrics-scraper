import requests, time

class spotifyDict(dict):
    def formatLyrics(self, mode: int = 0): return formatLyrics(self, mode)

def getToken(sp_dc: str, sp_key: str = None) -> dict:
    """
    Generates a Spotify Auth Token for searching lyrics/track IDs.\n
    To obtain the sp_key and sp_dc, please check the README on PyPi.

    Returns:
        dict - {"token": "x", "expiry": 0}\n
        dict - {"status": False, "message": "error message", "data": "data"}
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "App-Platform": "WebPlayer",
        "content-type": "text/html; charset=utf-8",
    }
    cookies = {"sp_dc": sp_dc}
    if sp_key: cookies["sp_key"] = sp_key
    
    r = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player", headers=headers, cookies=cookies)
    print(r.json())
    if r.json()["isAnonymous"] == False: return {"token": r.json()["accessToken"], "expiry": r.json()["accessTokenExpirationTimestampMs"]}
    else: return {"status": False, "message": "Error while trying to grab Spotify token.", "data": r.text}

def checkExpiry(info: dict) -> dict:
    """
    Check the expiry of your token.

    Arguments:
        info {dict} - Information (contains token and expiry)\n
    """
    if info["expiry"] > round(time.time()-3*1000): return {"expired": False}
    return {"expired": True}

def formatLyrics(lyrics: dict, mode: int = 0) -> dict:
    """
    Format the lyrics to your liking with several modes.

    Arguments:
        lyrics {dict} - Takes the direct output from the getLyrics function. Needs the lyrics in the base spotify format.\n
        mode {int} - Choose which mode to format the lyrics in.\n
            - 0: Lyrics Only
            - 1: Milliseconds Start and Lyrics
            - 2: Seconds Start and Lyrics
    """

    if "message" not in lyrics: return {"status": False, "message": "No lyrics were provided or they were not in the correct format."}
    if "status" in lyrics:
        if not lyrics["status"]: return {"status": False, "message": "That JSON data is invalid because the status is set to false."}

    toReturn = []
    if mode == 1 or mode == 2:
        if lyrics["message"]["lyrics"]["syncType"] != "LINE_SYNCED": return {"status": False, "message": "Timestamps do not work on songs that aren't line synced."}
    
    if mode == 0:
        for element in lyrics["message"]["lyrics"]["lines"]:
            if str(element["words"]) == "": continue
            toReturn.append(str(element["words"]).replace("\\", ""))
        return {"status": True, "message": toReturn}
    if mode == 1:
        for element in lyrics["message"]["lyrics"]["lines"]:
            if str(element["words"]) == "": continue
            toReturn.append({"milliseconds": str(element["startTimeMs"]), "line": str(element["words"]).replace("\\", "")})
        return {"status": True, "message": toReturn}
    if mode == 2:
        for element in lyrics["message"]["lyrics"]["lines"]:
            if str(element["words"]) == "": continue
            toReturn.append({"seconds": str(round(int(element["startTimeMs"])/1000, 2)), "line": str(element["words"]).replace("\\", "")})
        return {"status": True, "message": toReturn}

    return {"status": False, "message": "That is not a valid format type."}

def getLyrics(info: dict, trackId: str = None, songName: str = None, proxies: dict = {}) -> spotifyDict:
    """
    Search up lyrics of any given song. Uses trackId first over songName.

    Arguments:
        info {dict} - Information (contains token and expiry)\n
        trackId {string} - The track ID for the Spotify song to search up.\n
        songName {string} - The song name to search up.\n
        proxies {dict} - Supports Socks5 and HTTP/S, example: {"http": "http://1.1.1.1:80", "https": "https://1.1.1.1:443", "http": "socks5://1.1.1.1:443"}

    Returns:
        dict - {"status": False if error, True if success, "message": "Reason why/lyrics"}
    """

    if not trackId and not songName: return {"status": False, "message": "No data was provided to search up."}
    
    if "expiry" and "token" not in info: return {"status": False, "message": "The key 'expiry' or 'value' was not found in the info dict."}

    tempCheck = checkExpiry(info)
    if tempCheck["expired"] == True: return {"status": False, "message": "Cookie has expired."}

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
        "App-Platform": "WebPlayer",
        "Authorization": f"Bearer {info['token']}"
    }

    if songName:
        try: r = requests.get(f"https://api-partner.spotify.com/pathfinder/v1/query?operationName=searchDesktop&variables=%7B%22searchTerm%22%3A%22{songName.replace(' ', '+')}%22%2C%22offset%22%3A0%2C%22limit%22%3A10%2C%22numberOfTopResults%22%3A5%2C%22includeAudiobooks%22%3Afalse%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22130115162add6f3499d2f88ead8a37a7cad1d4d2314f3a206377035e7d26b74c%22%7D%7D", headers=headers, proxies=proxies)
        except Exception as e: return {"status": False, "message": f"Error occured: {e}"}

        try: trackId = r.json()["data"]["searchV2"]["tracksV2"]["items"][0]["item"]["data"]["id"]
        except Exception as e: return {"status": False, "message": f"Error occured: {e} - song doesn't exist?"}

    if trackId:

        try: r = requests.get(f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{trackId}?format=json&market=from_token", headers=headers, proxies=proxies)
        except Exception as e: return {"status": False, "message": f"Error occured: {e}"}

        if '"lines"' in r.text: return spotifyDict({"status": True, "message": r.json()})
        else: return {"status": False, "message": f"Could not find track/Spotify responded with status: {r.status_code}, text: {r.text}"}
