#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
version = "1.5.0"
import importlib.metadata as metadata
import subprocess
import sys
import argparse
import logging_setup
import logging

# DEPENDENCY CHECK
def checkDependencies(logger):
    """
    Checks if the dependencies are installed.
    If not found, it will attempt to install them.

    Parameters
    ----------
    logger : logging.Logger
        The logger object.
    """
    logger.info("Checking dependencies...")
    try:
        metadata.version("ytmusicapi")
    except metadata.PackageNotFoundError:
        logger.error("ytmusicapi not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ytmusicapi"])
    try:
        metadata.version("pylast")
    except metadata.PackageNotFoundError:
        logger.error("pylast not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pylast"])
    logger.info("Dependencies are installed.")

def initialize():
    """
    Automated initialization for ReplayMix+. Checks command line arguments and runs the appropriate function.
    """
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(description="Automated Console for ReplayMix+")
    parser.add_argument("-p", "--playlist", action="store_true", help="Updates the ReplayMix+ Playlist.")
    parser.add_argument("-c", "--compendium", action="store_true", help="Updates the Compendium.")
    parser.add_argument("-vb", "--verbose", action="store_true", help="Enables verbose logging.")
    args = parser.parse_args()
    # Logging Setup
    # Change the False to True if you want verbose debug logging.
    verbose = False
    if args.verbose:
        verbose = True
    logging_setup.setup_logger(verbose)
    logger = logging.getLogger('rpmplusLogger')
    # Initialization
    logger.info(f" - - - ReplayMix+ Automated Console {version} - - - ")
    logger.info("Checking dependencies...")
    checkDependencies(logger)
    import generator_engine as gE
    import compendium_engine as cE
    logger.info("Dependencies are installed.")
    if args.compendium:
        logger.info("Updating Compendium...")
        cE.loadAllPlaylists()
    if args.playlist:
        logger.info("Updating Playlist...")
        gE.recreatePlaylist()
    logger.info("Exiting...")
    
initialize()