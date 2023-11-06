
"""
Module for generating random pet names from a large set.
call get_random_name()
The names are stored in the default file src/static/pages/names.txt,
but this can be overridden with a sitedef for installations that want to change it.
"""

import random

from asm3.sitedefs import RANDOM_NAME_FILE

names = []

def _load_names() -> None:
    global names
    if len(names) > 0: return
    with open(RANDOM_NAME_FILE, "r") as f:
        names = f.read().split("\n")

def get_random_name() -> str:
    """ Returns a random name from the list """
    global names
    _load_names()
    return random.choice(names)

def get_random_single_word_name() -> str:
    """ Returns only names that are a single word """
    while True:
        name = get_random_name()
        if name.find(" ") == -1 and name.strip() != "":
            return name
