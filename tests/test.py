#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.abspath(file_path))

import yatg


class TestHtmlTableConverter(unittest.TestCase):
    def setUp(self):
        self.samples_path = os.path.join(file_path, 'tests', 'samples')

    def test_html_table_to_emacs(self):
        succ_num = 0
        fail_num = 0
        for file in os.listdir(self.samples_path):
            if file.endswith('.html'):
                html_path = os.path.join(self.samples_path, file)
                fo = open(html_path, "r")
                data = fo.read()
                fo.close()

                # test html table to emacs table
                result = yatg.html_2_ascii_table(data, 'emacs')
                emacs_fn = os.path.splitext(file)[0] + '.emacs'
                emacs_path = os.path.join(self.samples_path, emacs_fn)
                emacs_fo = open(emacs_path, 'r')
                expect = emacs_fo.read()
                emacs_fo.close()
                fail_msg = "Convert {0} to emacs table failed, result is\n{1}, but expect:\n{2}".format(
                    file, result, expect)
                try:
                    self.assertEqual(result.rstrip(), expect.rstrip(),
                                     fail_msg)
                    succ_num += 1
                except AssertionError:
                    fail_num += 1
                    print(fail_msg)
        self.assertEqual(fail_num, 0,
                         "Failed {0} emacs table cases".format(fail_num))

    def test_html_table_to_orgmode(self):
        succ_num = 0
        fail_num = 0
        for file in os.listdir(self.samples_path):
            if file.endswith('.html'):
                html_path = os.path.join(self.samples_path, file)
                fo = open(html_path, "r")
                data = fo.read()
                fo.close()

                # test html table to orgmode table
                result = yatg.html_2_ascii_table(data, 'orgmode')
                orgmode_fn = os.path.splitext(file)[0] + '.orgmode'
                orgmode_path = os.path.join(self.samples_path, orgmode_fn)
                orgmode_fo = open(orgmode_path, 'r')
                expect = orgmode_fo.read()
                orgmode_fo.close()
                fail_msg = "Convert {0} to orgmode table failed, result is\n{1}, but expect:\n{2}".format(
                    file, result, expect)
                try:
                    self.assertEqual(result.rstrip(), expect.rstrip(),
                                     fail_msg)
                    succ_num += 1
                except AssertionError:
                    fail_num += 1
                    print(fail_msg)
        self.assertEqual(fail_num, 0,
                         "Failed {0} orgmode table cases".format(fail_num))

    def test_html_table_to_mysql(self):
        succ_num = 0
        fail_num = 0
        for file in os.listdir(self.samples_path):
            if file.endswith('.html'):
                html_path = os.path.join(self.samples_path, file)
                fo = open(html_path, "r")
                data = fo.read()
                fo.close()

                # test html table to orgmode table
                result = yatg.html_2_ascii_table(data, 'mysql')
                mysql_fn = os.path.splitext(file)[0] + '.mysql'
                mysql_path = os.path.join(self.samples_path, mysql_fn)
                mysql_fo = open(mysql_path, 'r')
                expect = mysql_fo.read()
                mysql_fo.close()
                fail_msg = "Convert {0} to mysql table failed, result is\n{1}, but expect:\n{2}".format(
                    file, result, expect)
                try:
                    self.assertEqual(result.rstrip(), expect.rstrip(),
                                     fail_msg)
                    succ_num += 1
                except AssertionError:
                    fail_num += 1
                    print(fail_msg)
        self.assertEqual(fail_num, 0,
                         "Failed {0} mysql table cases".format(fail_num))

    def test_html_table_to_markdown(self):
        succ_num = 0
        fail_num = 0
        for file in os.listdir(self.samples_path):
            if file.endswith('.html'):
                html_path = os.path.join(self.samples_path, file)
                fo = open(html_path, "r")
                data = fo.read()
                fo.close()

                # test html table to markdown table
                result = yatg.html_2_ascii_table(data, 'markdown')
                markdown_fn = os.path.splitext(file)[0] + '.markdown'
                markdown_path = os.path.join(self.samples_path, markdown_fn)
                markdown_fo = open(markdown_path, 'r')
                expect = markdown_fo.read()
                markdown_fo.close()
                fail_msg = "Convert {0} to markdown table failed, result is\n{1}, but expect:\n{2}".format(
                    file, result, expect)
                try:
                    self.assertEqual(result.rstrip(), expect.rstrip(),
                                     fail_msg)
                    succ_num += 1
                except AssertionError:
                    fail_num += 1
                    print(fail_msg)
        self.assertEqual(fail_num, 0,
                         "Failed {0} markdown table cases".format(fail_num))


    def test_csv_to_orgmode(self):
        succ_num = 0
        fail_num = 0
        for file in os.listdir(self.samples_path):
            if file.endswith('.csv'):
                html_path = os.path.join(self.samples_path, file)
                fo = open(html_path, "r")
                data = fo.read()
                fo.close()

                # test html table to orgmode table
                result = yatg.csv_2_ascii_table(data, ',', 'orgmode')
                orgmode_fn = os.path.splitext(file)[0] + '.orgmode'
                orgmode_path = os.path.join(self.samples_path, orgmode_fn)
                orgmode_fo = open(orgmode_path, 'r')
                expect = orgmode_fo.read()
                orgmode_fo.close()
                fail_msg = "Convert {0} to orgmode table failed, result is\n{1}, but expect:\n{2}".format(
                    file, result, expect)
                try:
                    self.assertEqual(result.rstrip(), expect.rstrip(),
                                     fail_msg)
                    succ_num += 1
                except AssertionError:
                    fail_num += 1
                    print(fail_msg)
        self.assertEqual(fail_num, 0,
                         "Failed {0} orgmode table cases".format(fail_num))

if __name__ == '__main__':
    unittest.main()
