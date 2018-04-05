"""YATG (Yet Another Table Generator).

A utility for generating ASCII art table.

Input data can be CSV or html, supports multiple output styles: orgmode, emacs,
mysql, markdown.
"""
from .yatg import html_2_ascii_table, csv_2_ascii_table, main_entry

def run_main():
    main_entry()
