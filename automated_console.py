#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
version = "1.6.1"
import pkg_resources
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
    valid = True
    with open("requirements.txt", 'r') as file:
        requirements = pkg_resources.parse_requirements(file)
        for requirement in requirements:
            try:
                pkg_resources.require(str(requirement))
            except pkg_resources.DistributionNotFound:
                valid = False  # A dependency is missing
            except pkg_resources.VersionConflict:
                valid = False  # Version conflict exists
    if not valid:
        logger.error("One or more dependencies are missing. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

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