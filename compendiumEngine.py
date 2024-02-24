"""
Replay Mix+ by soreikomori
v1.0.0
https://github.com/soreikomori/ReplayMixPlus
"""
from ytmusicapi import YTMusic
import json

def removeDuplicates(playlistTracks, compendium):
    """
    Checks a compendium and the tracks in a playlist and adds new tracks to it.

    :param playlistTracks: A list with ytmusicapi tracks (dictionaries).
    :param compendium: a compendium (list) usually fetched from ytm_compendium.json.
    :return: The updated compendium with new tracks added.

    """
    for track in playlistTracks:
        if track not in compendium:
            compendium.append(track)
    return compendium

def loadJson(filename):
    """
    Loads a .json file.

    :param filename: str with the json filename.
    :return: The loaded .json, or None if it was empty (or threw an error).
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except json.decoder.JSONDecodeError as e:
        return None

def writeIntoJson(content, filename):
    """
    Writes into a .json file.

    :param content: Whatever that is supposed to be written. In this program's context this is either a dict or a list.
    :param filename: str with the json filename.
    """
    with open(filename, 'w') as file:
        json.dump(content, file)

def loadAllPlaylists():
    """
    Loads all playlists in a user's account into the compendium. This includes any regular playlist in the library, Liked Music, and the history.
    """

    compendium = loadJson("ytm_compendium.json")
    if compendium == None:
        compendium = []
    yt = YTMusic("oauth.json")
    history = yt.get_history()
    playlists = yt.get_library_playlists()
    for playlist in playlists:
        id = playlist["playlistId"]
        playlist = yt.get_playlist(id, None)
        compendium = removeDuplicates(playlist["tracks"], compendium)
    removeDuplicates(history, compendium)
    writeIntoJson(compendium, "ytm_compendium.json")
    
