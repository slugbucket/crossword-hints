#!/usr/bin/env python3
"""Blog scraper

Script to download an HTML page and scrape crossword grid details

Recognises the following connabd line arguments:
* -b/--blogger - tha name of the blog post author (determines which scraper function to call)
* -d/--debug - verbose output
  -h/--help - descriptive help
  -s/--setter - name of the grid setter. Associates the clue with a setter in the database
"""
import logging
import sqlite3
import sys
from os import environ

import requests
from arg_parse import parse_args
from grid_bloggers import grid_bloggers

# Get the list of bloggers and setters from teh database
setters = ["crosophile", "filbert", "harold", "kairos", "monk", "phi", "tees"]

logger = logging.getLogger(__name__)


def get_setter_id(conn: object, setter: str) -> int:
    """Get the database id of a clue setter"""
    curs = conn.cursor()
    (sid,) = curs.execute(
        "SELECT rowid FROM crossword_setters WHERE name LIKE ?",
        (setter,),
    ).fetchone()
    return sid


def main(opts):
    """Main function
    Processes command args and calls the scraper funtion for the blogger
    """
    if opts.blogger not in grid_bloggers.bloggers:
        logger.error(f"Blogger {opts.blogger} cannot be found")
        sys.exit(1)
    conn = sqlite3.connect("../crossword_hints.db")
    sid = get_setter_id(conn, opts.setter)
    if not sid:
        logger.error(f"Setter {opts.setter} cannot be found")
        sys.exit(1)
    resp = requests.get(
        "https://www.fifteensquared.net/2020/05/05/independent-10471-by-vigo/",
        timeout=30,
    )
    html_doc = resp.text
    with open(opts.url, "r", encoding="utf-8") as f:
        html_doc = f.read()
    solve = getattr(grid_bloggers, "indy_" + opts.blogger)
    clues = solve(html_doc)
    for clue in clues:
        print(
            f'clue: {clue["clue"]}, solution: {clue["solution"]}, parse: {clue["parse"]}'
        )


def config_logger(dbg: bool) -> None:
    """Configure logger"""
    # logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if dbg or environ.get("DEBUG") == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


if __name__ == "__main__":
    args = parse_args()
    config_logger(args.debug)
    main(args)
