# -*- coding: utf-8 -*-
"""Argument parser

"""
from __future__ import annotations

import argparse


def parse_args():
    """Argument parser

    Processes the recognised command options
    """
    parser = argparse.ArgumentParser(
        description="Retrieve clues, solutions and parsing for a particular crossword puzzle"
    )
    parser.add_argument(
        "-b",
        "--blogger",
        help="Name of grid blogger",
        dest="blogger",
        default="",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="More verbose script output for debugging purposes",
        action=argparse.BooleanOptionalAction,
        default=False,
        required=False,
    )
    parser.add_argument(
        "-s",
        "--setter",
        help="Name of crossword setter",
        dest="setter",
        default="",
        type=str,
        required=True,
    )
    parser.add_argument(
        "url",
        metavar="URL_to_scrape",
        type=str,
        help="URL to be scraped for crossword puzzle soluton and parsing",
    )

    args, _ = parser.parse_known_args()
    return args
