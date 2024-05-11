#!/usr/bin/env python3
"""
"""

import argparse
import logging
import requests
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from arg_parse import parse_args
from os import environ
from grid_bloggers import grid_bloggers

# Get the list of bloggers and setters from teh database
setters = ["crosophile", "filbert", "monk", "phi", "tees"]

logger = logging.getLogger(__name__)


def main(args: object) -> None:
    if args.blogger not in grid_bloggers.bloggers:
        logger.error(f"Blogger {args.blogger} cannot be found")
        sys.exit(1)
    if args.setter not in setters:
        logger.error(f"Setter {args.setter} cannot be found")
        sys.exit(1)
    # resp = requests.get("https://www.fifteensquared.net/2020/05/05/independent-10471-by-vigo/")
    # html_doc = resp.text
    f = open(args.url, "r")  # for Quirister
    html_doc = f.read()
    solve =  getattr(grid_bloggers, 'indy_' + args.blogger)
    clues = solve(html_doc)
    for clue in clues:
        print(f'clue: {clue["clue"]}, solution: {clue["solution"]}, parse: {clue["parse"]}')


def config_logger(args: argparse.Namespace):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if args.debug or environ.get("DEBUG") == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

if __name__ == "__main__":
    args = parse_args()
    config_logger(args)
    main(args)