====
YATG
====

YATG (Yet Another Table Generator) is a utility for generating ASCII art table.

Introduction
============

This tool can convert csv or html to ASCII art table.

Example of output (emacs style)::

  +---------+-----------------+----------+
  |         | Average         | Red eyes |
  |         +--------+--------+          |
  |         | height | weight |          |
  +---------+--------+--------+----------+
  | Males   | 1.9    | 0.003  | 40%      |
  +---------+--------+--------+----------+
  | Females | 1.7    | 0.002  | 43%      |
  +---------+--------+--------+----------+

Example of output (orgmode style)::

  | Header content 1 | Header content 2 |
  |------------------+------------------|
  | Body content 1   | Body content 2   |
  | Body content 3   | Body content 4   |
  | Body content 5   | Body content 6   |

Example of output (mysql style)::

  +------------------+------------------+
  | Header content 1 | Header content 2 |
  +------------------+------------------+
  | Body content 1   | Body content 2   |
  | Body content 3   | Body content 4   |
  | Body content 5   | Body content 6   |
  +------------------+------------------+

Example of output (markdown style)::

  | Header content 1 | Header content 2 |
  |------------------|------------------|
  | Body content 1   | Body content 2   |
  | Body content 3   | Body content 4   |
  | Body content 5   | Body content 6   |

Installation
============

To install YATG from PyPI::

  $ pip install yatg

Or from github::

  $ curl -O https://raw.githubusercontent.com/10gic/yatg/master/yatg/yatg.py && chmod u+x yatg.py

Usage
=====

Options::

  usage: yatg [-h] [-i INFILE] [-f FORMAT] [-d DELIMITER] [-o OUTFILE]
              [-s STYLE] [--no-header] [--column-align ALIGN]
              [--width1-chars CHARS]

  Yet Another Table Generator, convert CSV or html table to ASCII art table.

  optional arguments:
    -h, --help            show this help message and exit
    -i INFILE, --input-file INFILE
                          source file, read from stdin if not specified
    -f FORMAT, --input-format FORMAT
                          format of input file, can be 'html' or 'csv', auto
                          guess it if not specified
    -d DELIMITER, --csv-delimiter DELIMITER
                          delimiter of csv data, guess it if not specified
    -o OUTFILE, --output-file OUTFILE
                          output file, write to stdout if not specified
    -s STYLE, --output-style STYLE
                          specify output table style, support 'orgmode',
                          'emacs', 'mysql', 'markdown', default is orgmode style
    --no-header           horizontal header line would not be printed if this
                          option present
    --column-align ALIGN  specify align string of columns, support 'l/r'. For
                          example, 'llrr' specify first two colums align left,
                          3rd and 4th columns align right. Default alignment is
                          left.
    --width1-chars CHARS  specify chars that should consider one character width
                          by force, only 'emoji' is supported currently. emoji
                          is considered as WIDE in unicode, but most terminal
                          render it only one character wide, you can set
                          --width1-chars=emoji to make output aligned in your
                          terminal

Feature
=======

- Support colspan and rowspan.
- Support multi output styles: emacs/orgmode(default)/mysql/markdown style.
- Table is keep aligned when cell contains both ASCII and non-ASCII charaters.
- Support custom column alignment.
- Header line is optional.
- Compatible with Python 2 and Python 3, tested in Python 2.6/2.7/3.6.
- No 3rd-part dependency (option ``--width1-chars=emoji`` require package emoji).

Limitation
==========

- Multi-line text in one table cell would flatten to one line.
- Nested tables are not supported.
