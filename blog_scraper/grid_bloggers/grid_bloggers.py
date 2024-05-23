# -*- coding: utf-8 -*-
"""Scraping crossword grid clues and solutions

This script defines functions that attempt to take an HTML page from an external blog
and scrape the crossword clues, solutions and parsing after stripping any HTML tags.

The function names correspond to the names of blog post authers.

The file is intended to be imported as a module
"""
import logging
import re
from html.parser import HTMLParser


bloggers = [
    "beermagnet",
    "bertandjoyce",
    "john",
    "john2",
    "kitty",
    "nealh",
    "quirister",
    "ratkojariku",
    "mc_rapper67",
]

logger = logging.getLogger(__name__)


class HTMLStripper(HTMLParser):
    """HTML Stripper class
    Defines class methods and variables used for handling HTML entities and data
    """

    convert_charrefs = True

    def __init__(self):
        """Class constructor"""
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        """Class method to handle data"""
        self.fed.append(data)

    def handle_entityref(self, name):
        """Class method for handling entity refs"""
        self.fed.append(f"&{name};")

    def get_data(self):
        """Class method to return data as a string"""
        return "".join(self.fed)


def indy_quirister(html_doc: str) -> list:
    """
    The clues are in the format:
    * 2 blank lines
    * clue# linelist[2]
    * solution linelist[3]
    * blank line
    * clue (n) linelist[5]
    * 3 blank lines
    * parse (repeat until blank line; start of next clue) linelist[10+]
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    # print(f"Using HTMLStripper on {html_doc}")
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    p = ""  # Empty string for possible multiline parsing
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            break
        if re.search(r"ACROSS", line):
            logger.debug("Found start of the across clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"DOWN", line):
            logger.debug("Found start of the down clues")
            in_the_clues = True
            lct = 0
            linelist = []
            continue
        if in_the_clues:
            if lct > 9 and not re.search(r"^$", line):  # Multiline parse
                p = p + linelist[lct - 1]
            if lct > 9 and re.search(r"^$", line):  # Start of next clue block
                p = p + linelist[lct - 1]
                c = re.sub(r" \([\d,-]+\)$", "", linelist[5])
                clue_list.append({"clue": c, "solution": linelist[3], "parse": p})
                linelist = []
                lct = 0
                p = ""
            linelist.append(line)
            lct = lct + 1
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_john(html_doc: str) -> list:
    """
    The clues are in the format:
    * 2 blank lines
    * clue# linelist[0]
    * solution linelist[1]
    * clue (solution length) linelist[2]
    * 4 blank lines
    * parsing linelist[3]
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    # print(f"Using HTMLStripper on {html_doc}")
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            logger.debug("Reached the end of the clues")
            in_the_clues = False
            break
        if re.search(r"ACROSS|Across", line):
            logger.debug("Found the start of the across clues")
            in_the_clues = True
            linelist = []
            lct = 0
            continue
        if re.search(r"DOWN|Down", line):
            logger.debug("Found the start of the down clues")
            in_the_clues = True
            linelist = []
            lct = 0
            continue
        if re.search(r"^$", line) and lct == 0:
            continue
        if re.search(r"^[0-9]+$", line):
            logger.debug(f"Found a clue block for {line}")
            lct = 1
            linelist.append(line)
            continue
        if in_the_clues and lct > 0:
            # There are blank lines in the clue block to be ignored
            if re.search(r"^$", line):
                continue
            logger.debug(f"Found a solution fragment, {line}, in clue line {lct}")
            linelist.append(line)
            lct = lct + 1
            if lct > 3:  # solution , clue and parse have been collected
                logger.debug(f"On line {lct} save the solution and parsing")
                c = re.sub(r" \([\d,-]+\)", "", linelist[2])
                clue_list.append(
                    {"clue": c, "solution": linelist[1], "parse": linelist[3]}
                )
                logger.debug(f"Adding {c} to the list of {len(clue_list)} clues")
                linelist = []
                lct = 0
                continue
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_john2(html_doc: str) -> list:
    """
    The clues are in the format:
    * 2 blank lines
    * clue# clue - SOLUTION
      (e.g. 1 Comic writer’s unhappiness about Dutch Royal family — WODEHOUSE) linelist[0]
    * parsing linelist[1]
    From:
    * https://www.fifteensquared.net/2020/06/19/141494/
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    # print(f"Using HTMLStripper on {html_doc}")
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    # logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            logger.debug("Reached the end of the clues")
            in_the_clues = False
            break
        if re.search(r"ACROSS|Across", line):
            logger.debug("Found the start of the across clues")
            in_the_clues = True
            linelist = []
            lct = 0
            continue
        if re.search(r"DOWN|Down", line):
            logger.debug("Found the start of the down clues")
            in_the_clues = True
            linelist = []
            lct = 0
            continue
        if re.search(r"^$", line) and lct == 0:
            continue
        if re.search(r"^[0-9]+", line) and in_the_clues:
            logger.debug(f"Found a clue block for {line}")
            lct = 1
            linelist.append(line)
            continue
        if in_the_clues and lct > 0:
            logger.debug(f"Found a solution fragment, {line}, in clue line {lct}")
            linelist.append(line)
            lct = lct + 1
            if lct > 1:  # solution , clue and parse have been collected
                ncs = re.match(r"^(\d+) (.*) ([A-Z ]+)$", linelist[0])
                if ncs:
                    clue_list.append(
                        {"clue": ncs[2], "solution": ncs[3], "parse": linelist[1]}
                    )
                else:
                    logger.error(f"Could not process clue from {linelist[0]}")
                linelist = []
                lct = 0
                continue
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_bertandjoyce(html_doc: str) -> list:
    """
    The clues are in the format:

    ACROSS

    1 Means to rescue European snake trapped by elevators (9)
    LIFEBOATS

    E (European) BOA (snake) in or ‘trapped by’ LIFTS (elevators)

    6 Italian from Ancona boxes (5)
    ROMAN

    Hidden in or ‘boxed by’ fROM ANcona
    ...


    DOWN

    1 Liberal drinks, loses head and uses borrowed money to pay for company (9)
    LEVERAGES

    L (Liberal) bEVERAGES (drinks) without the first letter or ‘head’

    2 Fool losing heart over total wager ( 7)
    FLUTTER

    FooL (without the middle letters or ‘heart’) UTTER (total)
    ...
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    bct = 0  # blank line count
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if in_the_clues and lct < 5:
            linelist.append(line)
            lct = lct + 1
            if in_the_clues and lct == 5:
                linelist.pop(0)
                linelist.pop(2)
                c = re.sub(r"\([\d,-]+\)$", "", linelist[0])
                clue_list.append(
                    {"clue": c, "solution": linelist[1], "parse": linelist[2]}
                )
                linelist = []
                lct = 0
                bct = 0
        if re.search(r"Across|ACROSS", line):
            in_the_clues = True
            linelist = []
            lct = 0
            bct = 0
            continue
        if re.search(r"Down|DOWN", line):
            in_the_clues = True
            linelist = []
            lct = 0
            bct = 0
            continue
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            # print(f"No more clues with {bct}")
            break
        if re.search(r"^$", line):
            bct = bct + 1
            if bct > 2:
                in_the_clues = False
                linelist = []
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_nealh(html_doc: str) -> list:
    """
    The clues are in the format:
    * 2 blank lines
    * clue# linelist[2]
    * solution linelist[3]
    * clue (n) linelist[4]
    * 4 blank lines
    * parse (repeat until blank line; start of next clue) linelist[9+]
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    p = ""  # Empty string for possible multiline parsing
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            break
        if re.search(r"Across|ACROSS", line):
            logger.debug("Found start of the across clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"Down|DOWN", line):
            logger.debug("Found start of the down clues")
            in_the_clues = True
            lct = 0
            linelist = []
            continue
        if in_the_clues:
            if lct > 9 and not re.search(r"^$", line):  # Multiline parse
                p = p + linelist[lct - 1]
            if lct > 9 and re.search(r"^$", line):  # Start of next clue block
                p = p + linelist[lct - 1]
                c = re.sub(r" \([\d,-]+\)$", "", linelist[4])
                clue_list.append({"clue": c, "solution": linelist[3], "parse": p})
                linelist = []
                lct = 0
                p = ""
            linelist.append(line)
            lct = lct + 1
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_ratkojariku(html_doc: str) -> list:
    """
    The clues are in the format:
    * 7 blank lines (+2 under the Acroos and Down markers)
    * clue# linelist[0]
    * solution linelist[1]
    * clue linelist[2]
    * parse (repeat until blank line; start of next clue) linelist[9+]
    Example posts:
    * https://www.fifteensquared.net/2020/06/17/independent-10508-tees/
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    chdr = 0  # counter to skip extra lines at the start of the section marker
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            chdr = 2
            break
        if re.search(r"Across", line):
            in_the_clues = True
            lct = 0
            chdr = 2
            continue
        if re.search(r"Down", line):
            in_the_clues = True
            lct = 0
            continue
        if chdr > 0:  # Skip two lines
            chdr = chdr - 1
            continue
        if re.search(r"^$", line):
            continue
        if re.search(r"^[0-9][0-9]$", line):
            lct = 1
            linelist = []
            continue
        if in_the_clues and lct > 0:
            if lct > 3:  # solution , clue and parse have been collected
                clue_list.append(
                    {"clue": linelist[1], "solution": linelist[0], "parse": linelist[2]}
                )
                linelist = []
                lct = 0
                continue
            linelist.append(line)
            lct = lct + 1
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_mc_rapper67(html_doc: str) -> list:
    """
    The clues are in the format:
    * 2 blank lines
    * clue# [0-9][0-9] linelist[0]
    * solution linelist[1]
    * clue linelist[2]
    * definition linelist[3]
    * parse linelist[4]
    The table starts with 5 column headers in plan text that don't trigger
    because the first line doesn't start with 2 digits
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            break
        if re.search(r"Across", line):
            logger.debug("Found start of the across clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"Down", line):
            logger.debug("Found start of the down clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"^$", line) and lct == 0:
            continue
        if re.search(r"^[0-9]+[AD]$", line):
            lct = 1
            linelist = []
            continue
        if in_the_clues and lct > 0:
            if lct > 4:  # solution , clue and parse have been collected
                c = re.sub(r" \([\d,-]+\)$", "", linelist[1])
                clue_list.append(
                    {"clue": c, "solution": linelist[0], "parse": linelist[3]}
                )
                linelist = []
                lct = 0
                continue
            linelist.append(line)
            lct = lct + 1
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_kitty(html_doc: str) -> list:
    """
    The clues are in the format:
    * clue# clue (solution length) linelist[0]
    * solution linelist[1]
    * parse linelist[2]
    * Sometimes a blank line
    The table starts with 5 column headers in plan text that don't trigger
    because the first line doesn't start with 2 digits
    Params:
        html_doc: str containing the full HTML document
    Returns:
        list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            break
        if re.search(r"ACROSS|Across", line):
            logger.debug("Found start of the across clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"DOWN|Down", line):
            logger.debug("Found start of the down clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"^$", line) and lct == 0:
            continue
        if re.search(r"^[0-9]+[ad][ ]+", line):
            logger.debug(f"Found a clue block for {line}")
            lct = 1
            linelist.append(line)
            continue
        if in_the_clues and lct > 0:
            logger.debug(f"Found a solution fragment, {line}, in clue line {lct}")
            linelist.append(line)
            lct = lct + 1
            if lct > 2:  # solution , clue and parse have been collected
                logger.debug(f"On line {lct} save the solution and parsing")
                c = re.sub(r"^[0-9]+[ad][ ]+", "", linelist[0])
                c = re.sub(r" \([\d,-]+\)", "", c)
                s = re.sub(r"^[ ]+", "", linelist[1])
                clue_list.append({"clue": c, "solution": s, "parse": linelist[2]})
                logger.debug(f"Adding {c} to the list of {len(clue_list)} clues")
                linelist = []
                lct = 0
                continue
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list


def indy_beermagnet(html_doc: str) -> list:
    """
        The clues are in the format:
        * 2 blank lines
        * clue# linelist[0]
        * solution (x,y) linelist[1]
        * parse linelist[2]

        Across


    1
    SLEEPING PARTNER
    He’ll go to bed with you, but his involvement is strictly financial (8,7)
    A Double Def. combining a literal and a figurative meaning into a suggestive scene.  First one in.
        From:
        * https://www.fifteensquared.net/2020/05/16/independent-10481-sat-16-may-2020-by-morph/
        Params:
            html_doc: str containing the full HTML document
        Returns:
            list of dicts: [ {"clue": .., "solution": .., "parse": ..}, {...}]
    """
    s = HTMLStripper()
    s.feed(html_doc)
    in_the_clues = False
    logger.debug(s.get_data())
    lct = 0  # in-clue line count; clue, solution and parsing spread over 5 lines
    clue_list = []
    linelist = []
    for line in s.get_data().splitlines():
        if re.search(r"^Categories .*", line):  # No more clues after this line
            in_the_clues = False
            break
        if re.search(r"ACROSS|Across", line):
            logger.debug("Found start of the across clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"DOWN|Down", line):
            logger.debug("Found start of the down clues")
            in_the_clues = True
            lct = 0
            continue
        if re.search(r"^$", line) and lct == 0:
            continue
        if re.search(r"^[0-9]+$", line):
            lct = 1
            linelist = []
            continue
        if in_the_clues and lct > 0:
            if lct > 3:  # solution , clue and parse have been collected
                c = re.sub(r" \([\d,-]+\)[ ]?$", "", linelist[1])
                clue_list.append(
                    {"clue": c, "solution": linelist[0], "parse": linelist[2]}
                )
                linelist = []
                lct = 0
                continue
            linelist.append(line)
            lct = lct + 1
    logger.debug(f"The are {len(clue_list)} clues in the grid.")
    return clue_list
