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
    to operate with the lastFM Network. Code inspired from @akraus53 on Github. Kudos!

    Returns
    -------
    pylast.User
        The userSelf object that will be used to fetch the top tracks and recent tracks.
    """
    logger.info("Connecting to Last.FM Network...")
    lastFmCreds = jt.loadJson("lastfmcreds.json")
    network = pylast.LastFMNetwork(api_key=lastFmCreds['apikey'], api_secret=lastFmCreds['apisecret'],
                               username=lastFmCreds['username'],
                               password_hash=lastFmCreds['password'])
    userSelf = network.get_user(lastFmCreds['username'])
    logger.info("Connected to Last.FM Network, returning UserSelf.")
    return userSelf

############### IMPORT AND FETCHES ###############
def fetchTopTracks(userSelf):
    """
    Fetches the top tracks for a certain "period" of time for the user. Saves these in a list of TopItems.
    Note that period and limit have configurable value. Configure them as you like.

    Parameters
    ----------
    userSelf : pylast.User
        The userSelf function that lastFmNetworkConnect() returns.
    
    Returns
    -------
    list
        A list of TopItem objects.
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

    Parameters
    ----------
    userSelf : pylast.User
        The userSelf function that lastFmNetworkConnect() returns.

    Returns
    -------
    list
        A list of PlayedTrack objects.
    """
    #So far, this only supports 7 days according to the calculation below. I plan to add more days at a later version if there is demand for other timeframes.
    sevenDaysAgo = round(time.time() - (7 * 24 * 60 * 60))
    logger.info("Fetching recent tracks from Last.FM...")
    return userSelf.get_recent_tracks(time_from=sevenDaysAgo, limit=None)

############### MASTERLIST CREATION ###############
def createMasterList():
    """
    Creates the main list that will be put into YTM later. It works by getting all the info from other functions and then returning the list sorted by score.

    Returns
    -------
    list
        A list of dictionaries, each containing the track's title, artist, YTM ID and score. The list is sorted by score in descending order.
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

    Parameters
    ----------
    title : str
        The title of the track.
    artist : str
        The artist of the track. Currently unused.
    
    Returns
    -------
    str or None
        The videoId of the track in the compendium. None if the track is not found.
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

    Parameters
    ----------
    title : str
        The title of the track.
    recentTracks : list
        A list of recent tracks in the selected timestamp, generated by fetchRecentTracks.

    Returns
    -------
    int
        The maximum amount of repetitions for the given track. Returns 0 if the title is never found in recentTracks.
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

    Parameters
    ----------
    title : str
        The title of the track.
    recentTracks : list
        A list of recent tracks in the selected timestamp, generated by fetchRecentTracks.
    
    Returns
    -------
    int or None
        The unix timestamp of the last time the track was played. None if the title is never found in recentTracks.
    """
    for track in recentTracks:
        if track.track.get_title() == title:
            return track.__getattribute__("timestamp")
    return None

def calcScore(scrobbles, lastPlayed, repetitions, maxScrobbles, maxRepetitions):
    """
    Calculates the score of a track based on the algorithm in the return line.

    Parameters
    ----------
    scroVal : int
        The amount of scrobbles the track has.
    lpVal : int
        The unix timestamp of the last time the track was found in last.fm.
    repetitions : int
        The maximum amount of repetitions (uninterrupted loops) the track has.
    maxScrobbles : int
        The maximum scrobbles of any track in the selected timespan.
    maxRepetitions : int
        The maximum number of repetitions of any track in the selected timestamp.
    
    Returns
    -------
    int
        The calculated score of the track.
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
    Creates a YTM playlist given a name and a description. Raises an exception if it didn't work.

    Parameters
    ----------
    name : str
        The title of the playlist.
    desc : str
        The description of the playlist.

    Returns
    -------
    str
        The playlist ID of the newly created playlist.
    """
    return yt.create_playlist(name, desc)