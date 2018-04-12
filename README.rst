====
YATG
====

YATG (Yet Another Table Generator) is a utility for generating ASCII art table.

.. image:: https://travis-ci.org/10gic/yatg.svg?branch=master
    :target: https://travis-ci.org/10gic/yatg
    :alt: Build status

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

As command-line tool
--------------------
Options::

  usage: yatg [-h] [-i INFILE] [-f FORMAT] [-d DELIMITER] [-o OUTFILE]
              [-s STYLE] [--no-header] [--column-align ALIGN]
              [--width1-chars CHARS] [--align-in-tty]

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
                          by force, only 'emoji' is supported currently. This
                          option requires package emoji.
    --align-in-tty        set column aligned in tty. This option requires
                          package blessed. If this option present, option
                          --width1-chars would be ignored. NOTE: (1) this option
                          requires you in a tty, (2) each column width must less
                          than width of tty, please enlarge your tty window if
                          you have long cell data.

As a library
------------
Example::

  >>> import yatg
  >>> print(yatg.csv_2_ascii_table([["head1", "head2"],
  ... ["content1", "content2"],
  ... ["content3", "content4"]]))
  | head1    | head2    |
  |----------+----------|
  | content1 | content2 |
  | content3 | content4 |

  >>> print(yatg.html_2_ascii_table("""
  ... <table border="1">
  ...     <tr>
  ...         <td>1st row</td>
  ...         <td colspan=2>colspan2</td>
  ...         <td rowspan=2>rowspan2</td>
  ...     </tr>
  ...     <tr>
  ...         <td>2nd row</td>
  ...         <td>under colspan2</td>
  ...         <td>under colspan2</td>
  ...     </tr>
  ...     <tr>
  ...         <td>3rd row</td>
  ...         <td colspan=3>colspan3</td>
  ...     </tr>
  ... </table>""", output_style='emacs'))
  +---------+---------------------------------+----------+
  | 1st row | colspan2                        | rowspan2 |
  +---------+----------------+----------------+          |
  | 2nd row | under colspan2 | under colspan2 |          |
  +---------+----------------+----------------+----------+
  | 3rd row | colspan3                                   |
  +---------+--------------------------------------------+

Function doc::

  >>> print(yatg.csv_2_ascii_table.__doc__)
   Convert csv to ascii table.

      Arguments:
        csv_content: Data of input csv, can be string or 'list of list'.
        csv_delimiter: The delimiter of csv string data (default is ',').
        output_style: The output style: emacs|orgmode|mysql|markdown
                      (default is 'orgmode').
        column_align: align string of columns, support 'l/r'. For example,
                     'llrr' specify first two colums align left, 3rd and 4th
                     columns align right. Default alignment is left.
        no_header: whether print horizontal header line. Default is False
        align_in_tty: force align column in tty

      Returns:
        Ascii table

  >>> print(yatg.html_2_ascii_table.__doc__)
   Convert html table to ascii table.

      Arguments:
        html_content: Data of input html.
        output_style: The output style: emacs|orgmode|mysql|markdown
                      (default is 'orgmode').
        column_align: align string of columns, support 'l/r'. For example,
                     'llrr' specify first two colums align left, 3rd and 4th
                     columns align right. Default alignment is left.
        no_header: whether print horizontal header line. Default is False
        align_in_tty: force align column in tty

      Returns:
        Ascii table

Feature
=======

- Support colspan and rowspan.
- Support multi output styles: emacs/orgmode(default)/mysql/markdown style.
- Table is keep aligned when cell contains both ASCII and non-ASCII charaters.
- Support custom column alignment.
- Header line is optional.
- Compatible with Python 2 and Python 3.
- No 3rd-part dependency for major functions.

Limitation
==========

- Multi-line text in one table cell would flatten to one line.
- Nested tables are not supported.
