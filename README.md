    # ReplayMix+
ReplayMix+ is a playlist generator for YouTube Music inspired by the native Replay Mix. It addresses the limitations of the original Replay Mix by including all tracks in a user's library, including uploaded tracks, managing original and cover tracks, and avoiding ignoring tracks for no apparent reason.

![GitHub License](https://img.shields.io/github/license/soreikomori/ReplayMixPlus)
![GitHub Release](https://img.shields.io/github/v/release/soreikomori/ReplayMixPlus?color=%234287f5)

## Features
- Generates a custom playlist based on your last 7 days of last.fm listening history, including uploaded tracks.
- Organizes music based on listening frequency, recency, and loop count.
- One-click-run self-contained console for ease of use.

## Requirements
Python 3.8 or higher.

## Installation and Usage

Download the latest release from the [releases page](link-to-releases), then unzip it wherever you want and execute `ReplayMixPlusConsole.py`. This last file will also be your updater.

## FAQ

>  How does ReplayMix+ handle uploaded tracks?

ReplayMix+ includes all tracks in your library, including uploaded tracks, unlike the original Replay Mix. It does this by cross-checking the title between last.fm and YTM.

> How often are playlists generated?

Playlists can be generated at any time by running the console application and updating them. There are no set intervals for playlist generation, however- the process is currently manual.

> How does ReplayMix+ determine the playlist order?
ReplayMix+ uses a small algorithm that considers factors such as how frequently a track has been listened to, how recently it was listened to, and how many times it was listened to on loop.

> I feel like the algorithm is off, it prioritizes tracks that it shouldn't.

The algorithm for this is actually rather simple and based on the weight that you give to 3 variables: number of scrobbles, time since last scrobble, and number of playbacks on loop only. If you want to change the weights, take a look at the `calcScore` function in generatorEngine.py. There's a comment that tells you which values to change.

> Is there a limit to the size of the generated playlist? Can I change it?

100 tracks, currently. If you wish to change the size of the playlist, take a look at `fetchTopTracks()` in `generatorEngine.py`. I added some comments so you know what to change.

> Is there a GUI available?

No. ReplayMix+ uses a console-based interface for simplicity.

> I get an error when trying to register with Google!
 
This might happen depending on your browser or extensions. I use Firefox, for examlpe, and it never works for some reason, so I just copy the URL to Edge instead. Some tracker removal extensions can also meddle with the process, so you might want to try disabling them for a bit.

> Why do I have to input my last.fm password?

In order for the API to communicate with your last.fm and ask for data, it needs to authenticate that you're the one using it by using your password hashed with MD5. This means that, after you input it, it will be saved on lastfmcreds.json and will never leave your device- as pyLast will only communicate using the hashed version. 

> What's the "Compendium"?

It's the term I give a file called `ytm_compendium.json`. It pulls all of the tracks in all of your playlists so that no matter what you're listening to, it will have it at the ready to compare with the list of tracks from last.fm.

> How much space does this take up?

Everything except for the compendium doesn't take more than 200KB. The compendium is the heavy one, which depends on the amount of tracks on your playlists. It's somewhere around 1KB per track, maybe less. Mine has 16391 tracks and is around 7.6MB. So all in all not too much.

> Will this work for tracks not in the latin alphabet?

I haven't given it a try with every language, but I have some tracks in Japanese and Russian (Cyrillic) and it works. It's probably compatible with anything utf-8, but I don't know enough about Unicode stuffs to say for sure.

> I get "Could not find the track [track] in the Compendium.", what do I do?

**Update your compendium.**

If you still get the error, you might need to add the track to a playlist (or give it a thumbs up so it's on your Liked Music), or listen to it again so it shows up on your recent history (it only saves up to 200 tracks).

If you *still* get the error, well...

TL;DR: Title mismatch between last.fm and YTM, most possibly caused by scrobble editing. A possible fix is uploading the track as an Uploaded Song to your YTM.

Long explanation: This happens because the tracks in last.fm and YTM are matched by title only. This means that a certain track (the one on the error message) on your last.fm wasn't found in your YTM (in the compendium, to be precise). The only way this can happen is because of the scrobbles being edited in last.fm either by the service itself if you have pro, or by a scrobbler (or both). 

There are two things to be done here:

If the issue is with a video that has a name like "artist - track (cover)" or something of the sort, I suggest you make the track into an upload in YTM. Here's an example of what I did:

This is how the track used to look as a YouTube video:

![Screenshot](image-1.png)

I decided to download the track then apply some metadata magic to it, which resulted in this:

![alt text](image-2.png)

Now the title has been fixed and it shows up very well on my last.fm, also reducing the issue of the track being scrobbled with the previous track's album.

Do note, however, that if you do this, you won't be adding views to the original video anymore, which could hurt the artist. (In my case, I am subscribed to this artist's patreon and was able to download the song as a reward)

The solution then is storing these edits within ReplayMix+, something that I am planning to work on if there is a demand for it. If you feel like you need this, feel free to tell me on an issue and I will try to work on an idea. You could also help with a pull request if you're eager.
## Contribution

Feel free to make a pull request with anything you like. I'll take a look at some point. If you want to get more hands on with the project, contact `soreikomori` on Discord.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details. Note that pylast uses the Apache 2.0 license, also included [in their repo](https://github.com/pylast/pylast/blob/main/LICENSE.txt).

## Disclaimer
This project is not affiliated with or endorsed by YouTube Music.