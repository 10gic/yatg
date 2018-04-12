#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Yet Another Table Generator, convert CSV or html table to ASCII art table. """

__author__ = 'cig01'
__email__ = 'juhani@163.com'
__version__ = '0.11.2'
__source__ = 'https://github.com/10gic/yatg'
__license__ = 'AGPLv3+'

__all__ = ['html_2_ascii_table', 'csv_2_ascii_table', 'FORCE_WIDTH1_CHARS']

import sys
import unicodedata
import logging
import csv

try:
    from html.parser import HTMLParser  # Python 3
except ImportError:
    from HTMLParser import HTMLParser  # Python 2

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False

try:
    import blessed
    BLESSED_AVAILABLE = True
except ImportError:
    BLESSED_AVAILABLE = False

logger = logging.getLogger('app')
logging.basicConfig(
    format=
    "[%(filename)s:%(lineno)-3s:%(funcName)20s %(levelname)s] %(message)s",
    level=logging.INFO)

# Maximum number of rows that supported, you can enlarge it for big table
MAX_TABLE_ROWS = 500
# Maximum number of columns that supported, you can enlarge it for big table
MAX_TABLE_COLS = 100

FORCE_WIDTH1_CHARS = []


def width_from_term(s):
    """ Get width of s render in terminal, return -1 if not in a tty.
    NOTE: If width of s is large that term.width, you would get a truncate
    length, and the char(s) in term may not be clear!!! FIXME
    """
    term = blessed.Terminal()
    if not term.is_a_tty:
        return -1
    logger.debug("current term width = %d", str(term.width))

    with term.cbreak(), term.location(y=term.height - 1, x=0):
        _, y0 = term.get_location(timeout=5.0)  # store first position
        assert y0 != -1, "get_location return -1,-1, may be you not in a tty"
        sys.stdout.write(s)  # put char(s) to term
        _, y1 = term.get_location(timeout=5.0)  # store second position
        assert y0 != -1, "get_location return -1,-1, may be you not in a tty"
        horizontal_distance = y1 - y0  # determine distance
        sys.stdout.write(
            '\b \b' * horizontal_distance)  # clear char(s) in term
        return horizontal_distance


def wide_chars(s):
    """ Return the number of wide chars in string s. WIDE(W) and FULLWIDTH(F) is
    considered as wide chars. AMBIGUOUS(A), for example “”‘’, is not wide."""
    if 'emoji' in FORCE_WIDTH1_CHARS and EMOJI_AVAILABLE:
        # consider emoji as width 1 if it in FORCE_WIDTH1_CHARS
        return sum(x not in emoji.UNICODE_EMOJI and \
                   (unicodedata.east_asian_width(x) == 'W' or \
                    unicodedata.east_asian_width(x) == 'F') for x in s)
    return sum(
        unicodedata.east_asian_width(x) == 'W'
        or unicodedata.east_asian_width(x) == 'F' for x in s)


def width(s, align_in_tty):
    """ Return the width of string s."""
    # python 2, convert str to unicode. In python 3, str is unicode
    if sys.version_info[0] < 3 and isinstance(s, str):
        s = s.decode('utf-8')
    if align_in_tty and BLESSED_AVAILABLE:
        return width_from_term(s)
    return len(s) + wide_chars(s)


class MyTableCell:
    """ Represent cell in table """

    def __init__(self, data='', cell_type='th', attrs=None):
        self.data = data
        self.cell_type = cell_type
        self.attrs = attrs

    def get_colspan(self):
        if self.attrs is None:
            return 1
        for attr in self.attrs:
            if attr[0] == 'colspan':
                return int(attr[1])
        return 1  # default

    def get_rowspan(self):
        if self.attrs is None:
            return 1
        for attr in self.attrs:
            if attr[0] == 'rowspan':
                return int(attr[1])
        return 1  # default


class MyHTMLParser(HTMLParser):
    """ This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    Modified from https://github.com/schmijos/html-table-parser-python3
    """

    def __init__(
            self,
            data_separator='',
    ):
        HTMLParser.__init__(self)

        self._data_separator = data_separator

        self._in_td = False
        self._in_th = False
        self._in_tr = False
        self._attrs = []
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []

    def handle_starttag(self, tag, attrs):
        """ We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        # logger.debug("handle_starttag tag=[%s], attrs=%s", tag, attrs)
        if tag in ['td', 'th', 'tr']:
            # Handle the case of ignoring closing tag tr/th/td, for example:
            # <table border=1>
            #  <tr><th>row1,col1<th>row1,col2
            #  <tr><td>row2,col1<td>row2,col2
            # </table>
            if self._in_th:
                self.handle_endtag('th')
            elif self._in_td:
                self.handle_endtag('td')
            if tag == 'tr' and self._in_tr:
                self.handle_endtag('tr')
        if tag == 'td':
            self._in_td = True
        if tag == 'th':
            self._in_th = True
        if tag == 'tr':
            self._in_tr = True
        if tag in ['td', 'th']:
            self._attrs = attrs
        # Just convert <br> to one space
        if tag == 'br' and (self._in_td or self._in_th):
            self._current_cell.append(' ')

    def handle_data(self, data):
        """ This is where we save content to a cell """
        if self._in_td or self._in_th:
            # logger.debug("handle_data data=[%s]", data)
            self._current_cell.append(data)

    def handle_entityref(self, name):
        """ Handle HTML encoded characters &NAME, for example &gt;, &nbsp;
        Note: this function only called when python version < 3.5,
        In python 3.5+, HTMLParser(*, convert_charrefs=True), the default
        of convert_charrefs is True, handle_entityref is not called."""
        if name == 'nbsp':
            # self.unescape('&nbsp;') produce NO-BREAK SPACE(0xA0)
            # but, we need SPACE(0x20).
            unescaped = " "
        else:
            unescaped = self.unescape('&{0};'.format(name))
        self.handle_data(unescaped)

    def handle_charref(self, name):
        """ Handle HTML encoded characters &#NNN, for example &#62;
        Note: this function only called when python version < 3.5,
        In python 3.5+, HTMLParser(*, convert_charrefs=True), the default
        of convert_charrefs is True, handle_charref is not called."""
        if name == '160':
            # self.unescape('&#160;') produce NO-BREAK SPACE(0xA0)
            # but, we need SPACE(0x20).
            unescaped = " "
        else:
            unescaped = self.unescape('&#{0};'.format(name))
        self.handle_data(unescaped)

    def handle_endtag(self, tag):
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        # logger.debug("handle_endtag tag=[%s]", tag)
        if tag == 'table':
            # Handle the case of ignoring closing tag tr/th/td, for example:
            # <table border=1>
            #  <tr><th>row1,col1<th>row1,col2
            #  <tr><td>row2,col1<td>row2,col2
            # </table>
            if self._in_th:
                self.handle_endtag('th')
            elif self._in_td:
                self.handle_endtag('td')
            if self._in_tr:
                self.handle_endtag('tr')
        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False
        elif tag == 'tr':
            self._in_tr = False

        if tag in ['td', 'th']:
            final_cell = self._data_separator.join(self._current_cell).strip()
            final_cell = final_cell.replace('\r\n', \
                                    ' ').replace('\r', ' ').replace('\n', ' ')
            # Remove leading and tailing tab, replace tab in mid to one space
            final_cell = final_cell.strip('\t')
            final_cell = final_cell.replace('\t', ' ')
            self._current_row.append(MyTableCell(final_cell, tag, self._attrs))
            self._current_cell = []
            self._attrs = []
        elif tag == 'tr':
            self._current_table.append(self._current_row)
            self._current_row = []
        elif tag == 'table':
            self.tables.append(self._current_table)
            self._current_table = []


def dump_cell_types(table):
    """ Return cell type in table, just for debugging """
    out_str = ''
    for i, _ in enumerate(table):
        current_row = ""
        for j, _ in enumerate(table[i]):
            current_row += "None\t" if table[i][j] is None else table[i][j].cell_type + "\t"
        out_str += current_row + "\n"
    return out_str


class IncreaseUp(object):
    """ For generating auto-increase span id """

    def __init__(self, n):
        self.n = n

    def next(self):
        r = self.n
        self.n += 1
        return r


def gen_expand_table(origtable):
    """" The output of this function in an internal table, we use it to convert
    final output table. If output table likes:
    +--------------------+------+-------+--------+
    | Item / Desc.       | Qty. | @     | Price  |
    +--------------------+------+-------+--------+
    | Paperclips (Box)   | 100  | 1.15  | 115.00 |
    +--------------------+------+-------+--------+
    | Paper (Case)       | 10   | 45.99 | 459.90 |
    +--------------------+------+-------+--------+
    | Wastepaper Baskets | 2    | 17.99 | 35.98  |
    +--------------------+------+-------+--------+
    | Subtotal                          | 610.88 |
    +---------------------------+-------+--------+
    | Tax                       | 7%    | 42.76  |
    +---------------------------+-------+--------+
    | Total                             | 653.64 |
    +-----------------------------------+--------+
    Following cell_type would set in this function:
    th	th	th	th
    td	td	td	td
    td	td	td	td
    td	td	td	td
    span0	span0	span0	td
    span1	span1	td	td
    span2	span2	span2	td

    If the ID part in spanID is same, means it in same span cell.
    """
    logger.debug("origtable is:\n" + dump_cell_types(origtable))
    table_expand_spans = []
    for i in range(MAX_TABLE_ROWS):
        table_expand_spans.append([])
        for _ in range(MAX_TABLE_COLS):
            table_expand_spans[i].append(None)  # Initialize each cell to None

    span_id = IncreaseUp(0)

    pending_no_leader_span_cells = []
    for i in range(MAX_TABLE_ROWS):
        colspan_passed = 0

        # Check pending no leader span cells
        pending_span_cells_current_row = filter(lambda item: item[0] == i,
                                                pending_no_leader_span_cells)
        for item in pending_span_cells_current_row:
            logger.debug("normal span cell index is: %d, %d", item[0], item[1])
            colspan_passed += 1
            table_expand_spans[i][item[1]] = MyTableCell(None, item[2])
        if i > len(origtable) - 1:
            break
        for j, _ in enumerate(origtable[i]):
            colspan = origtable[i][j].get_colspan()
            assert colspan > 0, "Find colspan <= 0"
            rowspan = origtable[i][j].get_rowspan()
            assert rowspan > 0, "Find rowspan <= 0"

            try:
                # find index of first None cell, and insert data
                item_index = table_expand_spans[i].index(None)
                if colspan > 1 or rowspan > 1:
                    current_span_id = "span" + str(span_id.next())
                    table_expand_spans[i][item_index] = MyTableCell(
                        origtable[i][j].data, current_span_id,
                        origtable[i][j].attrs)
                else:
                    table_expand_spans[i][item_index] = origtable[i][j]
            except ValueError:  # If None is not found in table_expand_spans
                sys.stderr.write(
                    "Warn: your table has too many columns, only output partial result.\n"
                )
            for _ in range(colspan - 1):
                try:
                    # find index of first None cell, and insert spanID
                    item_index = table_expand_spans[i].index(None)
                    table_expand_spans[i][item_index] = MyTableCell(
                        None, current_span_id)
                except ValueError:  # If None is not found in table_expand_spans
                    sys.stderr.write(
                        "Warn: your table has too many columns, only output partial result.\n"
                    )
            # If current is leading span cell, save other cells in same span
            # unit into pending_no_leader_span_cells
            for x in range(rowspan - 1):
                for y in range(colspan):
                    logger.debug(
                        "add (%d,%d,%s) to pending_no_leader_span_cells",
                        i + x + 1, j + colspan_passed + y, current_span_id)
                    pending_no_leader_span_cells.append(
                        (i + x + 1, j + colspan_passed + y, current_span_id))
            colspan_passed += colspan - 1
    # shrink table_expand_spans
    max_rows = 0
    max_cols = 0
    for i in range(MAX_TABLE_ROWS):
        current_max_cols = 0
        for j in range(MAX_TABLE_COLS):
            if table_expand_spans[i][j] is not None:
                current_max_cols += 1
        if current_max_cols == 0:  # if entire row are None
            max_rows = i
            break
        if i == MAX_TABLE_ROWS - 1:
            sys.stderr.write(
                "Warn: your table has too many rows, only output partial result.\n"
            )
            max_rows = MAX_TABLE_ROWS
            break
        if current_max_cols > max_cols:
            max_cols = current_max_cols
    logger.debug("max_rows=%d, max_cols=%d", max_rows, max_cols)
    shrinked = [table_expand_spans[i][0:max_cols] for i in range(max_rows)]
    # If there is None cell in shrinked, change it to MyTableCell("", "none")
    # Following table is an example of this case
    # <table border="1">
    # <tr>
    #  <th>Header content 1</th>
    #  <th>Header content 2</th>
    # </tr>
    # <tr>
    #  <td>Body content 1</td>
    # </tr>
    # </table>
    for column in shrinked:
        for j, elem in enumerate(column):
            if elem is None:
                column[j] = MyTableCell("", "none")
    return shrinked


def is_span_cell(cell):
    """ Return true if cell has span type"""
    return cell.cell_type.startswith("span")


def is_leader_span_cell(cell):
    """ Return true if cell is the first(leader) span cell.
    Consider following table, There are 4 "cells" in each row.
    Pay attention to 4 cells in row 2.
    +-------------+------+-------+--------+
    |  Baskets    | 2    | 17.99 | 35.98  |
    +-------------+------+-------+--------+
    | Subtotal                   | 610.88 |
    +----------------------------+--------+
        ^            ^        ^
        |            |        |
     leader      continue    continue
    span cell    span cell   span cell
    """
    return cell.cell_type.startswith("span") and cell.data is not None


def is_continue_span_cell(cell):
    """ Return true if cell is span cell but not leader span cell"""
    return cell.cell_type.startswith("span") and cell.data is None


def is_same_span_id(cell1, cell2):
    """ Return true is cell1 and cell2 in same span"""
    return is_span_cell(cell1) and is_span_cell(cell2) \
           and cell1.cell_type == cell2.cell_type


def gen_output_cols_width(expand_table, output_style, align_in_tty):
    """ Compute the width of each col that can hold cell data"""
    assert output_style in ['emacs', 'orgmode', 'mysql', 'markdown']
    if not expand_table:
        return []
    num_cols = len(expand_table[0])
    cols_max_width = [0 for _ in range(num_cols)]  # 0 repeated num_cols times
    leader_cells_colspan_ge_2 = []
    for i, _ in enumerate(expand_table):
        for j, _ in enumerate(expand_table[i]):
            if is_leader_span_cell(expand_table[i][j]):
                if expand_table[i][j].get_colspan() == 1:
                    if width(expand_table[i][j].data,
                             align_in_tty) > cols_max_width[j]:
                        cols_max_width[j] = width(expand_table[i][j].data,
                                                  align_in_tty)
                else:
                    leader_cells_colspan_ge_2.append(
                        (i, j, expand_table[i][j].get_colspan()))
            if not is_span_cell(expand_table[i][j]):
                assert expand_table[i][j].get_colspan() == 1, \
                    "Colspan must be 1 in normal cell"
                if width(expand_table[i][j].data,
                         align_in_tty) > cols_max_width[j]:
                    cols_max_width[j] = width(expand_table[i][j].data,
                                              align_in_tty)
    logger.debug("leader_cells_colspan_ge_2=%s", leader_cells_colspan_ge_2)
    spans = [x[2] for x in leader_cells_colspan_ge_2]  # x[2] is colspan value
    spans = sorted(set(spans))
    for span in spans:
        assert span >= 2, "Span of cell in leader_cells_colspan_ge_2 must >=2"
        leader_cells = [x for x in leader_cells_colspan_ge_2 if x[2] == span]
        for cell in leader_cells:
            ind_i = cell[0]
            ind_j = cell[1]
            if output_style == 'emacs':
                spans_widths = cols_max_width[ind_j:ind_j + span]
                total_width = sum(spans_widths) + (span - 1) * len(" | ")
                width_diff = total_width - \
                             width(expand_table[ind_i][ind_j].data, align_in_tty)
                # If content is span is to long, increase width of last cell
                # in same span
                if width_diff < 0:
                    logger.debug("width_diff=%d", width_diff)
                    cols_max_width[ind_j + span - 1] += -width_diff
            else:
                width_diff = cols_max_width[ind_j] - \
                             width(expand_table[ind_i][ind_j].data, align_in_tty)
                # If content is span is to long, increase width of first cell
                # in same span
                if width_diff < 0:
                    logger.debug("width_diff=%d", width_diff)
                    cols_max_width[ind_j] += -width_diff
    logger.debug("cols_max_width=%s", cols_max_width)
    return cols_max_width


def output_emacs_table(table, cols_max_width, column_align, align_in_tty):
    if not table:
        return ""
    alignment = ['l' for _ in range(MAX_TABLE_COLS)]  # default is left align
    if column_align:
        if len(column_align) > MAX_TABLE_COLS:
            column_align = column_align[0:MAX_TABLE_COLS]
        for index, item in enumerate(column_align):
            alignment[index] = item
    out_str = ''
    for i, _ in enumerate(table):
        # output horizontal line
        for j, _ in enumerate(table[i]):
            # output first character in horizontal line
            if i == 0:  # first row
                if j > 0 and is_same_span_id(table[i][j - 1], table[i][j]):
                    out_str += "-"
                else:
                    out_str += "+"
            else:
                if j == 0:  # first col
                    if is_same_span_id(table[i - 1][j], table[i][j]):
                        out_str += "|"
                    else:
                        out_str += "+"
                else:  # here, i>0, j>0
                    if is_same_span_id(table[i - 1][j - 1], table[i][j]):
                        out_str += " "
                    elif is_same_span_id(table[i - 1][j - 1], table[i - 1][j]) \
                         and is_same_span_id(table[i][j - 1], table[i][j]):
                        out_str += "-"
                    else:
                        out_str += "+"
            if i > 0 and is_same_span_id(table[i - 1][j], table[i][j]):
                out_str += " " * (1 + cols_max_width[j] + 1)
            else:
                out_str += "-" * (1 + cols_max_width[j] + 1)
        # last character in horizontal line
        if i > 0 and is_same_span_id(table[i - 1][len(table[i]) - 1],
                                     table[i][len(table[i]) - 1]):
            out_str += "|\n"
        else:
            out_str += "+\n"
        # output content
        for j, _ in enumerate(table[i]):
            # output first character
            if j == 0:
                out_str += "|"
            else:  # j > 0
                if i == 0:
                    if is_same_span_id(table[i][j - 1], table[i][j]):
                        # output nothing, there is leading span in previous cell
                        pass
                    else:
                        out_str += "|"
                else:  # i > 0
                    if is_same_span_id(table[i][j - 1], table[i][j]):
                        if is_same_span_id(table[i - 1][j], table[i][j]):
                            out_str += " "
                        else:
                            # output nothing, there is leading span in previous cell
                            pass
                    else:
                        out_str += "|"
            if not is_span_cell(table[i][j]):
                data_width = width(table[i][j].data, align_in_tty)
                diff = cols_max_width[j] - data_width
                if alignment[j] == 'l':
                    content = " " + table[i][j].data + " " * diff + " "
                elif alignment[j] == 'r':
                    content = " " + " " * diff + table[i][j].data + " "
                else:
                    raise Exception(
                        'Found invalid column align char {0}'.format(
                            alignment[j]))
                # logger.debug("normal cell[%d][%d] content=[%s]", i, j, content)
                out_str += content
            elif is_leader_span_cell(table[i][j]):
                data_width = width(table[i][j].data, align_in_tty)
                cell_colspan = table[i][j].get_colspan()
                cell_width = sum(cols_max_width[j:j + cell_colspan]) + \
                             len("   ") * (cell_colspan - 1)
                diff = cell_width - data_width
                # logger.debug("cell_colspan=[%s]", cell_colspan)
                # logger.debug("cell_width=[%s]", cell_width)
                # logger.debug("diff=[%s]", diff)
                if alignment[j] == 'l':
                    content = " " + table[i][j].data + " " * diff + " "
                elif alignment[j] == 'r':
                    content = " " + " " * diff + table[i][j].data + " "
                else:
                    raise Exception(
                        'Found invalid column align char {0}'.format(
                            alignment[j]))
                out_str += content
            elif i > 0 and is_same_span_id(table[i - 1][j], table[i][j]):
                # output empty string for rowspan
                out_str += " " + " " * cols_max_width[j] + " "
        out_str += "|\n"
    # output last line of current table
    last_row = len(table) - 1
    for j, _ in enumerate(table[0]):
        if j > 0 and is_same_span_id(table[last_row][j - 1],
                                     table[last_row][j]):
            out_str += "-"
        else:
            out_str += "+"
        out_str += "-" * (1 + cols_max_width[j] + 1)
    out_str += "+\n"
    return out_str


def output_other_table(table, cols_max_width, output_style, column_align,
                       no_header, align_in_tty):
    r""" Output table to orgmode or mysql or markdown style.
    An example of orgmode style:
    | Name  | Phone | Age |
    |-------+-------+-----|
    | Peter |  1234 |  17 |
    | Anna  |  4321 |  25 |

    An example of mysql style:
    +-------+-------+-----+
    | Name  | Phone | Age |
    +-------+-------+-----+
    | Peter |  1234 |  17 |
    | Anna  |  4321 |  25 |
    +-------+-------+-----+

    An example of markdown style:
    | Name  | Phone | Age |
    |-------|-------|-----|
    | Peter |  1234 |  17 |
    | Anna  |  4321 |  25 |

    Note:
    Character | in cell will be escaped for orgmode/markdown style
    In orgmode table:  convert | to \vert
    In markdown table: convert | to \|
    """
    assert output_style in ['orgmode', 'mysql', 'markdown']
    if not table:
        return ""
    cols_max_width_new = list(cols_max_width)  # copy list
    if output_style == 'mysql':
        pass  # No escaping for |
    else:
        # Compute number of | in each column, we will escape it
        num_cols = len(table[0])
        nums_of_vert_bar = [0 for _ in range(num_cols)]
        for i, _ in enumerate(table):
            for j, _ in enumerate(table[i]):
                if is_leader_span_cell(
                        table[i][j]) or not is_span_cell(table[i][j]):
                    count = table[i][j].data.count('|')
                    if count > nums_of_vert_bar[j]:
                        nums_of_vert_bar[j] = count
        if output_style == 'orgmode':
            escaped = '\\vert'
        elif output_style == 'markdown':
            escaped = '\\|'
        multi = len(escaped)
        cols_max_width_new = \
            [a + multi * b for a, b in zip(cols_max_width, nums_of_vert_bar)]

    alignment = ['l' for _ in range(MAX_TABLE_COLS)]  # default is left align
    if column_align:
        if len(column_align) > MAX_TABLE_COLS:
            column_align = column_align[0:MAX_TABLE_COLS]
        for index, item in enumerate(column_align):
            alignment[index] = item
    out_str = ''
    for i, _ in enumerate(table):
        if i == 0 and output_style == 'mysql':
            # first horizontal line for mysql style
            for j, _ in enumerate(table[i]):
                if j == 0:
                    out_str += "+"
                else:
                    out_str += "+"
                out_str += "-" * (1 + cols_max_width_new[j] + 1)
            out_str += "+\n"
        if no_header:
            pass
        else:
            if i == 1:
                # output horizontal line
                for j, _ in enumerate(table[i]):
                    if j == 0:  # first character in horizontal line
                        if output_style == 'orgmode':
                            out_str += "|"
                        elif output_style == 'mysql':
                            out_str += "+"
                        elif output_style == 'markdown':
                            out_str += "|"
                    else:
                        if output_style == 'orgmode':
                            out_str += "+"
                        elif output_style == 'mysql':
                            out_str += "+"
                        elif output_style == 'markdown':
                            out_str += "|"
                    out_str += "-" * (1 + cols_max_width_new[j] + 1)
                # last character and newline in horizontal line
                if output_style == 'orgmode':
                    out_str += "|\n"
                elif output_style == 'mysql':
                    out_str += "+\n"
                elif output_style == 'markdown':
                    out_str += "|\n"
        # output content
        for j, _ in enumerate(table[i]):
            out_str += "|"
            if is_continue_span_cell(table[i][j]):
                content = " " + " " * cols_max_width_new[j] + " "
                out_str += content
            else:
                if output_style == 'mysql':
                    data_new = table[i][j].data
                else:
                    data_new = table[i][j].data.replace("|", escaped)
                data_width = width(data_new, align_in_tty)
                diff = cols_max_width_new[j] - data_width
                if alignment[j] == 'l':
                    content = " " + data_new + " " * diff + " "
                elif alignment[j] == 'r':
                    content = " " + " " * diff + data_new + " "
                else:
                    raise Exception(
                        'Found invalid column align char {0}'.format(
                            alignment[j]))
                out_str += content
        out_str += "|\n"
        if i == len(table) - 1 and output_style == 'mysql':
            # last horizontal line for mysql style
            for j, _ in enumerate(table[i]):
                if j == 0:
                    out_str += "+"
                else:
                    out_str += "+"
                out_str += "-" * (1 + cols_max_width_new[j] + 1)
            out_str += "+\n"
    return out_str


def gen_table_from_csv(csv_content, csv_delimiter):
    lines = csv_content.splitlines()
    data = csv.reader(lines, delimiter=csv_delimiter)
    ret_table = []
    for row in data:
        current_row = []
        if row:
            for element in row:
                current_row.append(MyTableCell(element, "csv"))
        ret_table.append(current_row)
    return ret_table


def gen_table_from_list(csv_content):
    """ In order to reuse function output_emacs_table/output_other_table
    We generate table contains cells with type MyTableCell"""
    ret_table = []
    for row in csv_content:
        current_row = []
        for col in row:
            current_row.append(MyTableCell(col, "csv"))
        ret_table.append(current_row)
    return ret_table


def _is_string(data):
    if sys.version_info[0] < 3:  # python 2
        return isinstance(data, basestring)
    return isinstance(data, str)


def csv_2_ascii_table(csv_content,
                      csv_delimiter=',',
                      output_style='orgmode',
                      column_align=None,
                      no_header=False,
                      align_in_tty=False):
    """ Convert csv to ascii table.

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
    """
    assert output_style in ['emacs', 'orgmode', 'mysql', 'markdown']
    if _is_string(csv_content):
        table = gen_table_from_csv(csv_content, csv_delimiter)
    elif isinstance(csv_content, list):
        table = gen_table_from_list(csv_content)
    else:
        raise Exception("Unsupported csv_content type")
    cols_max_width = gen_output_cols_width(table, output_style, align_in_tty)
    logger.debug("cols_max_width=%s", cols_max_width)
    output_str = ''
    if output_style == 'emacs':
        output_str += output_emacs_table(table, cols_max_width, column_align,
                                         align_in_tty)
    else:
        output_str += output_other_table(table, cols_max_width, output_style,
                                         column_align, no_header, align_in_tty)
    # logger.debug("Out put is:\n" + output_str)
    return output_str


def html_2_ascii_table(html_content,
                       output_style='orgmode',
                       column_align=None,
                       no_header=False,
                       align_in_tty=False):
    """ Convert html table to ascii table.

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
    """
    assert output_style in ['emacs', 'orgmode', 'mysql', 'markdown']
    output_str = ''
    parser = MyHTMLParser()
    parser.feed(html_content)
    for table in parser.tables:
        table_expand_spans = gen_expand_table(table)
        logger.debug("cell types of table_expand_spans:\n" +
                     dump_cell_types(table_expand_spans))
        cols_max_width = gen_output_cols_width(table_expand_spans,
                                               output_style, align_in_tty)
        logger.debug("cols_max_width=%s", cols_max_width)
        if output_style == 'emacs':
            output_str += output_emacs_table(
                table_expand_spans, cols_max_width, column_align, align_in_tty)
        else:
            output_str += output_other_table(
                table_expand_spans, cols_max_width, output_style, column_align,
                no_header, align_in_tty)
        output_str += "\n"  # output newline as the delimiter of multiple tables
    # With Python 3.6, &nbsp; &#160; would convert to NO-BREAK SPACE(0xA0) by
    # HTMLParser. I expect it just convert to SPACE(0x20).
    output_str = output_str if sys.version_info[0] < 3 \
                            else output_str.replace(chr(0xA0), chr(0x20))
    # logger.debug("Out put is:\n" + output_str)
    return output_str[:-1] if output_str.endswith("\n") else output_str


def main_entry():
    input_file = None
    input_format = None
    output_file = None
    output_style = 'orgmode'  # default
    csv_delimiter = None
    no_header = False
    column_align = None
    width1_chars = None
    align_in_tty = False
    try:
        import argparse  # argparse is introduced in Python 2.7 and Python 3.2
        arg_parser = argparse.ArgumentParser(
            description='Yet Another Table Generator, ' \
            'convert CSV or html table to ASCII art table.')
        arg_parser.add_argument(
            "-i",
            "--input-file",
            type=argparse.FileType('r'),
            help="source file, read from stdin if not specified",
            metavar='INFILE',
            dest="input_file")
        arg_parser.add_argument(
            "-f",
            "--input-format",
            help="format of input file, can be 'html' or 'csv', " \
                 "auto guess it if not specified",
            dest="input_format",
            metavar='FORMAT',
            choices=["html", "csv"])
        arg_parser.add_argument(
            "-d",
            "--csv-delimiter",
            help="delimiter of csv data, guess it if not specified",
            metavar='DELIMITER',
            dest="csv_delimiter")
        arg_parser.add_argument(
            "-o",
            "--output-file",
            help="output file, write to stdout if not specified",
            metavar='OUTFILE',
            dest="output_file")
        arg_parser.add_argument(
            "-s",
            "--output-style",
            help="specify output table style, support 'orgmode', 'emacs', " \
                 "'mysql', 'markdown', default is orgmode style",
            metavar='STYLE',
            default="orgmode",
            dest="output_style",
            choices=["emacs", "orgmode", "mysql", "markdown"])
        arg_parser.add_argument(
            '--no-header',
            help=
            "horizontal header line would not be printed if this option present",
            action='store_true',
            dest="no_header")
        arg_parser.add_argument(
            "--column-align",
            help="specify align string of columns, support 'l/r'. For " \
                 "example, 'llrr' specify first two colums align left, 3rd " \
                 "and 4th columns align right. Default alignment is left.",
            metavar='ALIGN',
            dest="column_align")
        arg_parser.add_argument(
            "--width1-chars",
            help="specify chars that should consider one character width by " \
                 "force, only 'emoji' is supported currently. This option " \
                 "requires package emoji.",
            metavar='CHARS',
            dest="width1_chars",
            choices=["emoji"])
        arg_parser.add_argument(
            "--align-in-tty",
            help="set column aligned in tty. This option requires package " \
                 "blessed. If this option present, option --width1-chars " \
                 "would be ignored. NOTE: (1) this option requires you in a " \
                 "tty, (2) each column width must less than width of tty, " \
                 "please enlarge your tty window if you have long cell data.",
            action='store_true',
            dest="align_in_tty")
        args = arg_parser.parse_args()
        input_file = args.input_file
        input_format = args.input_format
        output_file = args.output_file
        output_style = args.output_style
        csv_delimiter = args.csv_delimiter
        no_header = args.no_header
        column_align = args.column_align
        width1_chars = args.width1_chars
        align_in_tty = args.align_in_tty

    except ImportError:
        sys.stderr.write("Warn: Cannot import argparse. Read from stdin, " \
                         "convert to {0} style always\n".format(output_style))
    if column_align is not None:
        if column_align.replace("l", "").replace("r", ""):
            sys.stderr.write(
                "--column-align is not valid, only l/r is supported.\n")
            sys.exit(1)
    if width1_chars == 'emoji':
        if not EMOJI_AVAILABLE:
            sys.stderr.write("Error: force emoji be one character width require" \
                             " package emoji, please run `pip install emoji`.\n")
            sys.exit(1)
        FORCE_WIDTH1_CHARS.append('emoji')
    if align_in_tty:
        if not BLESSED_AVAILABLE:
            sys.stderr.write("Error: option --align-in-tty require package " \
                             "blessed, please run `pip install blessed`\n")
            sys.exit(1)
    if input_file:  # read from file
        input_content = input_file.read()
        input_file.close()
    else:  # read from stdin
        sys.stderr.write(
            "Info: read data from stdin, press Ctrl-D (i.e. EOF) when finished\n"
        )
        input_content = sys.stdin.read()
    if input_format is None:
        # Guess input_format is html if it starts with <
        if input_content.strip(" \r\n\t").startswith("<"):
            input_format = "html"
        else:
            input_format = "csv"
        logger.debug("Guess input_format as [%s]", input_format)
    if input_format == "csv" and csv_delimiter is None:
        # Guess csv_delimiter
        firstline = input_content.strip(" \r\n").split('\n', 1)[0]
        candidate = [",", "\t", ";", "|"]
        occurs = [firstline.count(c) for c in candidate]
        best_index = occurs.index(max(occurs))  # index of max item
        csv_delimiter = candidate[best_index]
        if firstline:  # not empty
            sys.stderr.write(
                "Info: auto set character [{0}] as csv_delimiter.\n".format(
                    csv_delimiter))
    out_content = ""
    if input_format == "html":
        out_content = html_2_ascii_table(input_content, output_style,
                                         column_align, no_header, align_in_tty)
    elif input_format == "csv":
        out_content = csv_2_ascii_table(input_content, csv_delimiter,
                                        output_style, column_align, no_header,
                                        align_in_tty)
    if out_content:
        if output_file is None:
            sys.stdout.write(out_content)
        else:
            outfile = open(output_file, 'w')
            outfile.write(out_content)
            outfile.close()
    else:
        sys.stderr.write("Warn: No table is generated, may be your input " \
                         "data is empty or unnormal.\n")


if __name__ == '__main__':
    main_entry()
