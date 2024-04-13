#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
from ytmusicapi import YTMusic
import time
import pylast
import logging
import json_tools as jt

############### PRERUN FUNCTIONS ###############
logger = logging.getLogger('rpmplusLogger')
yt = YTMusic("oauth.json")

############### SETUP FUNCTIONS ###############
def lastFmNetworkConnect():
    """
    Opens the .json with API secret info and loads it into a lastFm variable
    to operate with the lastFM Network. There is a lastfmcreds.json.example in the
    local directory that tells you how to set this up correctly.

    Code inspired from @akraus53 on Github. Kudos!
    """
    logger.info("Connecting to Last.FM Network...")
    lastFmCreds = jt.loadJson("lastfmcreds.json")
    network = pylast.LastFMNetwork(api_key=lastFmCreds['apikey'], api_secret=lastFmCreds['apisecret'],
                               username=lastFmCreds['username'],
                               password_hash=pylast.md5(lastFmCreds['password']))
    userSelf = network.get_user(lastFmCreds['username'])
    logger.info("Connected to Last.FM Network, returning UserSelf.")
    return userSelf

############### IMPORT AND FETCHES ###############
def fetchTopTracks(userSelf):
    """
    Fetches the top tracks for a certain "period" of time for the user. Saves these in a list of TopItems.
    Note that period and limit have configurable value. Configure them as you like.

    :param userSelf: The userSelf function that lastFmNetworkConnect() returns. 
    :return: A list of TopItem objects.
    """
    # NOTES FOR PERIOD
    # Accepted values: overall | 7day | 1month | 3month | 6month | 12month
    period = "7day"
    #### PLAYLIST SIZE
    # You can change this if you want your playlist to be bigger or smaller.
    # CHANGE THIS LINE -----
    limit = 100
    # ------------
    logger.info("Fetching top tracks from Last.FM...")
    return userSelf.get_top_tracks(period=period,limit=limit)

def fetchRecentTracks(userSelf):
    """
    Fetches all last.fm scrobbles for the past 7 days.
    Do note that this takes rather long.

    :param userSelf: The userSelf function that lastFmNetworkConnect() returns.
    :return: A list of PlayedTrack objects.
    """
    #So far, this only supports 7 days according to the calculation below. I plan to add more days at a later version if there is demand for other timeframes.
    sevenDaysAgo = round(time.time() - (7 * 24 * 60 * 60))
    logger.info("Fetching recent tracks from Last.FM...")
    return userSelf.get_recent_tracks(time_from=sevenDaysAgo, limit=None)

############### MASTERLIST CREATION ###############
def createMasterList():
    """
    Creates the main list that will be put into YTM later. It works by getting all the info from other functions and then returning the list sorted by score.

    :return: List with a dictionary per track, organized by each dictionary's "score" value.
    """
    # Declarations
    masterList = []
    
    # Imports
    userSelf = lastFmNetworkConnect()
    topTracks = fetchTopTracks(userSelf)
    recentTracks = fetchRecentTracks(userSelf)
    maxScrobbles = topTracks[0]._asdict()["weight"]
    maxRepetitions = max(repetitionChecker(track.track.get_title(),recentTracks) for track in recentTracks)
    uniqueIds = []

    # Engine
    logger.info("Creating MasterList...")
    for track in topTracks:
        tiAsDict = track._asdict()
        scrobbles = tiAsDict["weight"]
        title = tiAsDict["item"].get_title()
        logger.debug("MasterList - Processing track: " + title)
        artist = tiAsDict["item"].get_artist().get_name()
        # Currently the value in "artist" has no use, but I still leave it to make the dictionary more understandable. Feel free to remove it from here and from checkYTMId().
        lastPlayed = lastPlayedChecker(title, recentTracks)
        repetitions = repetitionChecker(title, recentTracks)
        score = calcScore(scrobbles, lastPlayed, repetitions, maxScrobbles, maxRepetitions)
        ytmId = checkYTMId(title, artist)
        logger.debug("Track: " + title + " | Score: " + str(score))

        if ytmId != None and ytmId not in uniqueIds:
            uniqueIds.append(ytmId)
            # Declare Dictionary
            trackDict = {
                "title": title,
                # "artist": artist,
                "ytmid": ytmId,
                "score": score
            }
            masterList.append(trackDict)
    logger.info("MasterList created.")
    return sorted(masterList, key=lambda x: x["score"], reverse=True)

def checkYTMId(title, artist):
    """
    Does a cross-check between last.fm and YTM to find the YTM ID of the specific track to be added to the playlist.
    
    :param title: An str with the title of the track.
    :param artist: An str with the first artist of the track. Currently unused.
    :return: An str with the videoId for the track in the compendium.
        If it's not found, it returns None, which eventually results in the track simply not being included.
    """
    compendium = jt.loadJson("ytm_compendium.json")
    for track in compendium:
        """ NOTE The commented line below checks if a given artist exists in a YTM Track's "artists" value.

        It's currently unused because artists between YTM and last.fm are a lot more
        prone to errors unlike titles (especially when working with multiple artists)
        and thus I decided to not use it.

        If you're looking at my code and want to add more verifications for each track to make
        sure the program gets the right one (for example if you have multiple tracks with the
        same name) then maybe this can help you.
        """
        # artistPresent = any(artist == artists['name'] for artists in track.get('artists', []))
        if title.lower() == track["title"].lower():
            return track["videoId"]
    print("Could not find the track \"" + title + "\" in the Compendium.")
    logger.error("Could not find the track \"" + title + "\" in the Compendium.")
    return None

############### SCORE CALCULATION ###############
def repetitionChecker(title, recentTracks):
    """
    Checks the maximum amount of repetitions (uninterrupted loops) for a given track.

    :param title: str with the title of a track.
    :param recentTracks: list of recent tracks in the selected timestamp, generated by fetchRecentTracks. 
    :return: An int with the maximum amount of repetitions. Returns 0 if the title is never found in recentTracks.
    """
    scrobbled = False
    count = 0
    max_count = 0
    for track in recentTracks:
        if track.track.get_title() == title:
            scrobbled = True
        else:
            scrobbled = False
        if scrobbled:
            count += 1
        else:
            if max_count < count:
                max_count = count
            count = 0
    return max_count

def lastPlayedChecker(title, recentTracks):
    """
    Finds the last time a track was played according to the recent tracks in last.fm.

    :param title: str with the title of a track.
    :param recentTracks: list of recent tracks in the selected timestamp, generated by fetchRecentTracks. 
    :return: An int with the unix timestamp of the last time the track was played. Returns None if it can't find it.
    """
    for track in recentTracks:
        if track.track.get_title() == title:
            return track.__getattribute__("timestamp")
    return None

def calcScore(scrobbles, lastPlayed, repetitions, maxScrobbles, maxRepetitions):
    """
    Calculates the score of a track based on the algorithm in the return line.

    :paranm scroVal: Int of scrobbles that the track has.
    :param lpVal: Str with the unix timestamp of the last time the track was found in last.fm.
    :param repetitions: Int with the maximum amount of repetitions (uninterrupted loops) the track has.
    :param maxScrobbles: Int of the maximum scrobbles of any track in the selected timespan.
    :param maxRepetitions: Int with the maximum number of repetitions of any track in the selected timestamp.
    :return: Int with the calculated score.
    """     
    # Calculations
    scroVal = scrobbles/maxScrobbles
    # 604800 is the amount of seconds in 7 days.
    lpVal = (time.time()-int(lastPlayed))/604800
    repVal = repetitions/maxRepetitions

    #### WEIGHTS
    # Note that these parameters are to be changed accordingly to what the user prefers the most.
    # I include my personal cocktail of weights, but feel free to change it as you see fit.
    # CHANGE THESE LINES -----
    scrobbleWeight = 1
    recenWeight = 0.7
    repetitionWeight = 0.50
    # ----------------------

    return scrobbleWeight*scroVal + recenWeight*(1-lpVal) + repetitionWeight*repVal

############### YTM IMPLEMENTATION ###############
def recreatePlaylist():
    """
    Empties the ReplayMix+ playlist then readds all items in the MasterList in order.
    This is the only function that this entire script needs to run to work independently, as it calls all other functions.
    It will work as long as a compendium exists, and the playlistId is set in config.json.
    """
    logger.info("Playlist Recreation started.")
    playlistId = jt.loadJson("config.json")["ytPlaylistId"]
    currentTracks = yt.get_playlist(playlistId, None).get("tracks") # type: ignore
    videoIdList = []
    masterList = createMasterList()
    for track in masterList:
        logger.debug("Playlist Recreation - Adding track " + track["title"] + " to the playlist.")
        videoIdList.append(track["ytmid"])
    if len(currentTracks) > 0:
        logger.info("Removing current tracks from the playlist. (Playlist was not empty.)")
        yt.remove_playlist_items(playlistId, currentTracks)
    logger.info("Adding new tracks to the playlist.")
    time.sleep(15)
    currentTracks = yt.get_playlist(playlistId, None).get("tracks") # type: ignore
    while len(currentTracks) == 0:
        logger.error("Playlist is empty. Retrying...")
        yt.add_playlist_items(playlistId, videoIdList)
        time.sleep(15)
        currentTracks = yt.get_playlist(playlistId, None).get("tracks")
    logger.info("Playlist Recreation finished.")

############### CONSOLE HELPER FUNCTIONS ###############

def createPlaylist(name, desc):
    """
    Creates a YTM playlist given a name and a description.

    :param name: An str with the title of the YTM playlist.
    :param desc: An str with the playlist's description.
    :return: An str with the new playlist's ID if succeeded. Raises an exception if it didn't work.
    """
    return yt.create_playlist(name, desc)