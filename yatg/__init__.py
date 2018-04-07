"""YATG (Yet Another Table Generator).

A utility for generating ASCII art table.

Input data can be CSV or html, supports multiple output styles: orgmode, emacs,
mysql, markdown.
"""
from .yatg import html_2_ascii_table, csv_2_ascii_table, FORCE_WIDTH1_CHARS, \
    main_entry, __author__, __version__, __email__, __source__, __license__


def run_main():
    main_entry()
