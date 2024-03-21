#!/usr/bin/env python3
"""
Replay Mix+ by soreikomori
https://github.com/soreikomori/ReplayMixPlus
"""
import logging
def setup_logger(verbose):
    """
    Sets up the logger for the program.

    :param verbose: A boolean that determines if the logger will be verbose.
    """
    logger = logging.getLogger("rpmplusLogger")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logHandler = logging.FileHandler("rpmplus.log")
    logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(logFormatter)
    logger.addHandler(logHandler)