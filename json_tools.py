#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
import json
import logging
import os
logger = logging.getLogger('rpmplusLogger')

def writeIntoJson(content, filename):
    """
    Writes into a .json file.

    Parameters
    ----------
    content : dict or list
        Whatever that is supposed to be written. In this program's context this is either a dict or a list.
    filename : str
        The json filename.
    """
    with open(filename, 'w') as file:
        logger.info("Wrote into " + filename)
        json.dump(content, file)

def loadJson(filename):
    """
    Loads a .json file.

    Parameters
    ----------
    filename : str
        The json filename.
    
    Returns
    -------
    dict or None
        The loaded .json file. None if the file was not found.
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            if data:
                return data
    except FileNotFoundError:
        logger.error("The file " + filename + " was not found.")
        return None
    except json.decoder.JSONDecodeError:
        logger.error("The file " + filename + " was empty.")
        return {}
    
def createJson(filename):
    """
    Creates an empty .json file with the name given. If the file already exists, it does nothing.

    Parameters
    ----------
    filename : str
        The json filename.
    """
    if not os.path.exists(filename):
        with open(filename, 'w') as json_file:
            json.dump({}, json_file)
        logger.info(filename + " created with empty dictionary.")
    else:
        logger.error(filename + " already exists.")