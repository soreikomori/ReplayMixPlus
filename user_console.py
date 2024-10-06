#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
version = "1.4.0"
import importlib.metadata as metadata
import subprocess
import sys
import os
import webbrowser
import logging_setup
import logging
import getpass
import json_tools as jt

# LOGGING SETUP
logging_setup.setup_logger(False)
logger = logging.getLogger('rpmplusLogger')
# INITIAL SETUP CHECKER
if jt.loadJson("config.json") == None or len(jt.loadJson("config.json")) == 0:
    firstSetupDone = False
else:
    firstSetupDone = True
    import generator_engine as gE
    import compendium_engine as cE
# PACKAGE CHECKER
if firstSetupDone:
    for package in ["pylast", "ytmusicapi"]:
        try:
            metadata.version(package)
        except metadata.PackageNotFoundError:
            confirmation = input(f"{package} is not installed. Would you like to install it? (y/n)")
            if confirmation.lower() == "y":
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            else:
                print("Please install the required packages before running the program.")
                exit()

def initialize():
    """
    User initialization for ReplayMix+. This leads to either the initial setup or the update, checking if the initial setup was done already or not.
    """
    logger.info(f" - - - ReplayMix+ User Console {version} - - -")
    print(f"ReplayMix+ Console {version} by soreikomori")
    print("")
    if not firstSetupDone:
        logger.info("config.json is empty. Running initial setup.")
        print("Welcome! It looks like this is your first time running the program.")
        print("If you press enter, you will go into the first setup.")
        print("If you had already set it up but you're still getting this, you should check your config.json file and the logs.")
        input("")
        initialSetup()
        return
    print("Hello! What would you like to do?")
    print("")
    repMenu = True
    while True:
        if repMenu:
            print("1 - Remake Initial Setup")
            print("2 - Update Playlist")
            print("3 - Exit")
            print("")
            print("Enter a number then press enter.")
            repMenu = False
        ans = input("")
        if ans == "1":
            initialSetup()
            return
        elif ans == "2":
            update()
            repMenu = True
        elif ans == "3":
            logger.info("Main Menu - Exiting...")
            return
        else:
            print("Invalid input.")
            repMenu = True

def initialSetup():
    """
    Performs the initial setup for ReplayMix+. Takes quite a while.
    """
    logger.info("- - Initial Setup Initialized - -")
    print("------------")
    print("INITIAL SETUP")
    print("")
    logger.info("Initial Setup Step 0: Packages")
    print("Step 0: Packages")
    print("")
    print("ReplayMix+ uses the pylast and ytmusicapi packages. They will be installed now. Press Enter after each installation.")
    print("")
    logger.info("Installing Dependencies...")
    installPyPackage("pylast")
    installPyPackage("ytmusicapi")
    print("")
    print("------------")
    logger.info("Initial Setup Step 1: Credentials")
    print("Step 1: Credentials")
    print("")
    print("In order to fetch data from both YouTube Music and last.fm, you will need to authenticate yourself in their websites.")
    print("Let's begin with YouTube Music, which uses oauth.")
    logger.info("YTM Authetication process started.")
    logger.info("Attempting to create oauth.json...")
    jt.createJson("oauth.json")
    if jt.loadJson("oauth.json") != None and len(jt.loadJson("oauth.json")) != 0:
        logger.error("YTM's oauth.json is not empty. Prompting user to skip or reauthenticate.")
        print("")
        print("Oh, it looks like you already have credentials- If you're repeating the initial setup and want to skip this step, type 1 then Enter.")
        print("If you want to authenticate again, type 2 then Enter.")
        while True:
            ans = input("")
            if ans == "1":
                break
            elif ans == "2":
                ytmIsAuthenticate()
                break
            else:
                print("Invalid input.")
    else:
        ytmIsAuthenticate()
    logger.info("YTM authentication complete.")
    import generator_engine as gE
    import compendium_engine as cE
    print("Now we authenticate last.fm.")
    logger.info("Last.fm Authetication process started.")
    logger.info("Attempting to create lastfmcreds.json...")
    jt.createJson("lastfmcreds.json")
    if jt.loadJson("lastfmcreds.json") != None and len(jt.loadJson("lastfmcreds.json")) != 0:
        logger.error("lastfmcreds.json is not empty. Prompting user to skip or reauthenticate.")
        print("")
        print("Ah, it looks like you already have credentials- If you're repeating the initial setup and want to skip this step, type 1 then Enter.")
        print("If you want to authenticate again, type 2 then Enter.")
        while True:
            ans = input("")
            if ans == "1":
                break
            elif ans == "2":
                lastfmIsAuthenticate()
                break
            else:
                print("Invalid input.")
    else:
        lastfmIsAuthenticate()
    logger.info("last.fm authentication complete.")
    print("Done!")
    print("If you think you put in the wrong thing, close the program and open it again.")
    print("")
    print("------------")
    logger.info("Initial Setup Step 2: Playlist Sync")
    print("Step 2: Playlist Sync")
    print("")
    print("Now you need to set up a YouTube Music Playlist to act as your ReplayMix+.")
    print("This step will create a private playlist. If you want to change the visibility, you can do so manually on YTM later.")
    logger.info("RPM+ Playlist creation process started.")
    succeeded = False
    while not succeeded:
        while True:
            logger.info("Prompting user for playlist name.")
            plName = input("Input the playlist name: ").strip()
            if plName == "" or plName == " ":
                logger.error("Playlist name empty, trying again.")
                print("Playlist name cannot be empty.")
            else:
                break
        logger.info("Prompting user for playlist description.")
        plDesc = input("Input the playlist description: ").strip()
        try:
            logger.info("Attempting to create playlist")
            playlistId = gE.createPlaylist(plName, plDesc)
            print("Playlist created succesfully!")
            logger.info("Playlist created successfully.")
            logger.info("Attempting to create config.json...")
            jt.createJson("config.json")
            jt.writeIntoJson({"ytPlaylistId": playlistId}, "config.json")
            succeeded = True
        except Exception as e:
            print("Something went wrong. You might want to try with a different name and/or description.")
            logger.error(f"Playlist creation failed. Exception: {e}. Trying again.")
    print("")
    print("------------")
    logger.info("Initial Setup Step 3: Compendium Setup")
    print("Step 3: Compendium Setup")
    print("")
    print("The Compendium is a list of all tracks in your library, including all your playlists and your history.")
    print("Note that it will need to be updated from time to time as you find new tracks and either put them in playlists (including liked songs) or listen to them.")
    print("If a compendium was already present, it will be updated.")
    logger.info("Compendium creation process started.")
    logger.info("Attempting to create ytm_compendium.json...")
    jt.createJson("ytm_compendium.json")
    print("Creating Compendium...")
    cE.loadAllPlaylists()
    print("Done.")
    print("")
    print("------------")
    logger.info("Initial Setup Step 4: ReplayMix+ Creation")
    print("Step 4: ReplayMix+ Creation")
    print("")
    print("Finally, the main part. The playlist will be created. To update it, run this same script. You'll get a different menu.")
    print("On the other hand, now that you have the .json files, you can run the automated console if you want to update the playlist without opening this script.")
    print("I suggest you update the playlist once per day, whether automatically or manually.")
    print("As for the compendium, you can update it whenever you want, but it's recommended to do it at least once a week, when you get errors about tracks not being found, or when you remember listening to new music recently.")
    print("Note that any errors about a track not being in the Compendium mean that the track's title on YTM and last.fm are different.")
    print("Check the FAQ for more info.")
    logger.info("ReplayMix+ creation process started.")
    logger.info("Creating ReplayMix+...")
    print("Creating ReplayMix+...")
    gE.recreatePlaylist()
    print("Done!")
    print("That is all. Enjoy!")
    input("Press enter to close.")
    logger.info("Initial Setup complete - Exiting...")

def ytmIsAuthenticate():
    """
    Authenticates YTM in the initial setup. This is a separate function because it's used twice. It also checks if the authentication was successful.
    """
    while True:
        logger.info("YTM authentication process started.")
        print("A new terminal window will open, which will prompt you to connect your Google account to an API.")
        print("Make sure to choose the right account that has your YTM library.")
        input("Press Enter to continue...")
        os.system("ytmusicapi oauth")
        print("")
        input("Once the authentication is done (you see a \"RefreshingToken\" response above), press Enter again.")
        print("")
        if len(jt.loadJson("oauth.json")) == 0:
            logger.error("YTM authentication failed.")
            print("Something went wrong- The credentials didn't save.")
            ans = input("Do you want to try again? Type 1 then Enter to try again, or 2 then Enter to close the console.")
            while True:
                if ans == "1":
                    logger.info("Retrying YTM authentication.")
                    break
                elif ans == "2":
                    logger.info("User chose to close the console.")
                    logger.info("Exiting program at YTM Authentication failure.")
                    exit()
                else:
                    print("Invalid input.")

def lastfmIsAuthenticate():
    """
    Authenticates lastfm in the initial setup. This is a separate function because it's used twice. It also checks if the authentication was successful.
    """
    import pylast
    logger.info("Last.fm authentication process started.")
    print("Note that this will require your username and password. You will have to paste them here.")
    print("First off is generating an API key for yourself.")
    print("You will be redirected to a website, where you will create an API account.")
    print("Just fill in the data. If you don't have a Callback URL or Application Homepage, you can leave those fields blank.")
    print("Once your account is created, you'll get an API Key and Shared Secret, which you will paste here.")
    input("Press Enter to open the Last.fm API website.")
    webbrowser.open("https://www.last.fm/api/account/create")
    print("")
    apiKey = getpass.getpass("Paste your API Key here: ").strip()
    shaSecret = getpass.getpass("Paste your Shared Secret here: ").strip()
    username = input("Input your last.fm username (case sensitive): ").strip()
    passwd = getpass.getpass("Input your last.fm password: ")
    logger.info("Last.fm Auth details written to lastfmcreds.json.")
    lastFmCreds = {"apikey": apiKey, "apisecret": shaSecret, "username": username, "password": pylast.md5(passwd)}
    jt.writeIntoJson(lastFmCreds, "lastfmcreds.json")

def update():
    """
    Performs an update of either the ReplayMix+ playlist, the Compendium, or both. 
    """
    print("---------")
    print("Would you like to update the ReplayMix+ only, or the Compendium as well?")
    print("")
    repMenu = True
    while True:
        if repMenu:
            print("1 - ReplayMix+ Only")
            print("2 - Compendium Only")
            print("3 - Compendium and ReplayMix+")
            print("4 - Return to Main Menu")
            print("")
        print("Enter a number then press enter.")
        ansUpdt  = input("")
        if ansUpdt == "1":
            logger.info("Executing update for playlist only.")
            print("Updating Playlist...")
            logger.info("Beginning playlist update...")
            gE.recreatePlaylist()
            logger.info("Playlist update complete.")
            print("Done.")
            print("--------")
            print("")
            repMenu = True
        elif ansUpdt == "2":
            logger.info("Executing update for compendium only.")
            logger.info("Beginning compendium update...")
            print("Updating Compendium...")
            cE.loadAllPlaylists()
            logger.info("Compendium update complete.")
            print("Done.")
            print("--------")
            print("")
            repMenu = True
        elif ansUpdt == "3":
            logger.info("Executing update for both playlist and compendium.")
            logger.info("Beginning compendium update...")
            print("Updating Compendium...")
            cE.loadAllPlaylists()
            logger.info("Compendium update complete.")
            print("Done.")
            logger.info("Beginning playlist update...")
            print("Updating Playlist...")
            gE.recreatePlaylist()
            logger.info("Playlist update complete.")
            print("Done.")
            print("--------")
            print("")
            repMenu = True
        elif ansUpdt == "4":
            return
        else:
            print("Invalid input.")
            repMenu = False

def installPyPackage(packageName):
    """
    Installs a python package to the user's python environment. Used for pyLast and ytmusicapi.

    Parameters
    ----------
    packageName : str
        The name of the package to be installed.
    """
    try:
        metadata.version(packageName)
        print(packageName + " is already installed.")
        logger.info(packageName + " is already installed.")
    except metadata.PackageNotFoundError:
        logger.error(packageName + " not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', packageName])
        print(packageName + " has been successfully installed.")
initialize()