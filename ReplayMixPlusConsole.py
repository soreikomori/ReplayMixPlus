"""
Replay Mix+ by soreikomori
v1.2.0
https://github.com/soreikomori/ReplayMixPlus
"""
import importlib.metadata as metadata
import subprocess
import sys
import os
import webbrowser
import json

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

if loadJson("config.json") == None:
    firstSetupDone = False
else:
    firstSetupDone = True
    import generatorEngine as gE
    import compendiumEngine as cE

def initialize():
    """
    Initialization for ReplayMix+. This leads to either the initial setup or the update, checking if the initial setup was done already or not.
    """
    print("ReplayMix+ Console v1.0.0")
    print("by soreikomori")
    print("")
    if not firstSetupDone:
        print("Welcome! It looks like this is your first time running the setup.")
        print("If you press enter, you will go into the first setup.")
        print("If you had already set it up but you're still getting this, you should check your config.json file.")
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
            return
        else:
            print("Invalid input.")
            repMenu = True

def initialSetup():
    """
    Performs the initial setup for ReplayMix+. Takes quite a while.
    """
    print("------------")
    print("INITIAL SETUP")
    print("")
    print("Step 0: Packages")
    print("")
    print("ReplayMix+ uses the pylast and ytmusicapi packages. They will be installed now. Press Enter after each installation.")
    print("")
    installPyPackage("pylast")
    installPyPackage("ytmusicapi")
    print("")
    print("------------")
    print("Step 1: Credentials")
    print("")
    print("In order to fetch data from both YouTube Music and last.fm, you will need to authenticate yourself in their websites.")
    print("Let's begin with YouTube Music, which uses oauth.")
    if loadJson("oauth.json") != None:
        print("")
        print("Oh, it looks like you already have credentials- If you're repeating the initial setup and want to skip this step, type 1 then Enter.")
        print("If you want to authenticate again, type 2 then Enter.")
        while True:
            ans = input("")
            if ans == "1":
                break
            elif ans == "2":
                print("A new terminal window will open, which will prompt you to connect your Google account to an API.")
                print("Make sure to choose the right account that has your YTM library.")
                input("Press Enter to continue...")
                os.system("ytmusicapi oauth")
                print("")
                input("Once the authentication is done (you see a \"RefreshingToken\" response above), press Enter again.")
                print("")
                break
            else:
                print("Invalid input.")
    else:
        print("A new terminal window will open, which will prompt you to connect your Google account to an API.")
        print("Make sure to choose the right account that has your YTM library.")
        input("Press Enter to continue...")
        os.system("ytmusicapi oauth")
        print("")
        input("Once the authentication is done (you see a \"RefreshingToken\" response above), press Enter again.")
        print("")
    import generatorEngine as gE
    import compendiumEngine as cE
    print("Now we authenticate last.fm.")
    if loadJson("lastfmcreds.json") != None:
        print("")
        print("Ah, it looks like you already have credentials- If you're repeating the initial setup and want to skip this step, type 1 then Enter.")
        print("If you want to authenticate again, type 2 then Enter.")
        while True:
            ans = input("")
            if ans == "1":
                break
            elif ans == "2":
                print("Note that this will require your username and password. You will have to paste them here.")
                print("First off is generating an API key for yourself.")
                print("You will be redirected to a website, where you will create an API account.")
                print("Just fill in the data. If you don't have a Callback URL or Application Homepage, you can leave those fields blank.")
                print("Once your account is created, you'll get an API Key and Shared Secret, which you will paste here.")
                input("Press Enter to open the Last.fm API website.")
                webbrowser.open("https://www.last.fm/api/account/create")
                print("")
                apiKey = input("Paste your API Key here: ").strip()
                shaSecret = input("Paste your Shared Secret here: ").strip()
                username = input("Input your last.fm username (case sensitive): ").strip()
                passwd = input("Input your last.fm password: ")
                lastFmCreds = {"apikey": apiKey, "apisecret": shaSecret, "username": username, "password": passwd}
                cE.writeIntoJson(lastFmCreds, "lastfmcreds.json")
                break
            else:
                print("Invalid input.")
    else:
        print("Note that this will require your username and password. You will have to paste them here.")
        print("First off is generating an API key for yourself.")
        print("You will be redirected to a website, where you will create an API account.")
        print("Just fill in the data. If you don't have a Callback URL or Application Homepage, you can leave those fields blank.")
        print("Once your account is created, you'll get an API Key and Shared Secret, which you will paste here.")
        input("Press Enter to open the Last.fm API website.")
        webbrowser.open("https://www.last.fm/api/account/create")
        print("")
        apiKey = input("Paste your API Key here: ").strip()
        shaSecret = input("Paste your Shared Secret here: ").strip()
        username = input("Input your last.fm username (case sensitive): ").strip()
        passwd = input("Input your last.fm password: ")
        lastFmCreds = {"apikey": apiKey, "apisecret": shaSecret, "username": username, "password": passwd}
        cE.writeIntoJson(lastFmCreds, "lastfmcreds.json")
    print("Done!")
    print("If you input the wrong thing, close the program and open it again.")
    print("")
    print("------------")
    print("Step 2: Playlist Sync")
    print("")
    print("Now you need to set up a YouTube Music Playlist to act as your ReplayMix+.")
    print("This step will create a private playlist. If you want to change the visibility, you can do so manually on YTM later.")
    succeeded = False
    while not succeeded:
        while True:
            plName = input("Input the playlist name: ").strip()
            if plName == "" or plName == " ":
                print("Playlist name cannot be empty.")
            else:
                break
        plDesc = input("Input the playlist description: ").strip()
        try: 
            playlistId = gE.createPlaylist(plName, plDesc)
            if isinstance(playlistId, str):
                print("Playlist created succesfully!")
                succeeded = True
                cE.writeIntoJson({"ytPlaylistId": playlistId}, "config.json")
            else:
                print("Something went wrong and I don't know what. Submit an issue in GitHub!")
                # No seriously, this either does exception or str. If it somehow doesn't do any of those then I genuinely have no clue what it is.
        except Exception as e:
            print("Something went wrong. You might want to try with a different name and/or description.")
    print("")
    print("------------")
    print("Step 3: Compendium Setup")
    print("")
    print("The Compendium is a list of all tracks in your library, including all your playlists and your history.")
    print("Note that it will need to be updated from time to time as you find new tracks and either put them in playlists (including liked songs) or listen to them.")
    print("Creating Compendium...")
    cE.loadAllPlaylists()
    print("Done.")
    print("")
    print("------------")
    print("Step 4: ReplayMix+ Creation")
    print("")
    print("Finally, the main part. The playlist will be created. To update it, run this same script. You'll get a different menu.")
    print("I suggest you update it once per day, whether automatically or manually.")
    print("Note that any errors about a track not being in the Compendium mean that the track's title on YTM and last.fm are different.")
    print("Check the FAQ for more info.")
    print("Creating ReplayMix+...")
    gE.recreatePlaylist()
    print("Done!")
    print("That is all. Enjoy!")
    input("Press enter to close.")

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
            print("Updating Playlist...")
            gE.recreatePlaylist()
            print("Done.")
            print("--------")
            print("")
            repMenu = True
        elif ansUpdt == "2":
            print("Updating Compendium...")
            cE.loadAllPlaylists()
            print("Done.")
            print("--------")
            print("")
            repMenu = True
        elif ansUpdt == "3":
            print("Updating Compendium...")
            cE.loadAllPlaylists()
            print("Done.")
            print("Updating Playlist...")
            gE.recreatePlaylist()
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

    :param packageName: The name of the package to be installed.
    """
    try:
        metadata.version(packageName)
        print(packageName + " is already installed.")
    except metadata.PackageNotFoundError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', packageName])
        print(packageName + " has been successfully installed.")
initialize()