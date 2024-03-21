#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
from ytmusicapi import YTMusic
import logging
import json_tools as jt
logger = logging.getLogger('rpmplusLogger')

def removeDuplicates(playlist, compendium):
    """
    Checks a compendium and the tracks in a playlist and adds non-duplicate tracks to it.
    To work correctly, this function needs to receive a PURGED playlist.

    :param playlist: A purged playlist with ytmusicapi tracks (dictionaries).
    :param compendium: a compendium (list) usually fetched from ytm_compendium.json.
    :return: The updated compendium with new tracks added.

    """
    for track in playlist:
        logger.debug("Duplicate Remover - Checking track " + track["title"])
        if track not in compendium:
            compendium.append(track)
    return compendium

def loadAllPlaylists():
    """
    Loads all playlists in a user's account into the compendium. This includes any regular playlist in the library, Liked Music, and the history.
    This function effectively creates or updates the entire compendium and it's the main function in this file.
    """
    compendium = jt.loadJson("ytm_compendium.json")
    if compendium == None:
        logger.info("Compendium was empty.")
        compendium = []
    yt = YTMusic("oauth.json")
    history = purgeFetchedPlaylist(yt.get_history())
    playlists = yt.get_library_playlists()
    logger.info("Loading playlists into compendium...")
    for playlist in playlists:
        logger.debug("Evaluating playlist " + playlist["title"])
        id = playlist["playlistId"]
        purgedPls = purgeFetchedPlaylist(yt.get_playlist(id, None)["tracks"]) # type: ignore
        logger.debug("Playlist fetched and purged.")
        compendium = removeDuplicates(purgedPls, compendium)
    removeDuplicates(history, compendium)
    resetCompendium()
    logger.info("Compendium updated.")
    jt.writeIntoJson(compendium, "ytm_compendium.json")

def purgeFetchedPlaylist(playlist):
    """
    Removes all track data except videoId, title, and artists for each track in a playlist.

    :param playlist: A playlist (dict) fetched from ytmusicapi.
    """
    purgedPlaylist = []
    logger.debug("Purging playlist...")
    for track in playlist:
        logger.debug("Purging track " + track["title"])
        purgedPlaylist.append({"videoId": track["videoId"], "title": track["title"], "artists": track["artists"]})
    return purgedPlaylist

def resetCompendium():
    """
    Resets the compendium by overwriting it with an empty list.
    """
    logger.info("Resetting compendium.")
    jt.writeIntoJson([], "ytm_compendium.json")