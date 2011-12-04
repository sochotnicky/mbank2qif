#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mbank2qif.py - mBank CSV output convertor to QIF (quicken) file
# Copyright (C) 2011  Stanislav Ochotnicky <stanislav@ochotnicky.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.

from contextlib import nested
import codecs
import sys
import csv

if len(sys.argv) != 3:
    print "Usage: %s input_file.csv output_file.qif" % sys.argv[0]
    sys.exit(1)

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

with nested(open(sys.argv[1], 'r'), open(sys.argv[2], 'w')) as (input, output):
    reader = codecs.getreader("cp1250")
    writer = codecs.getwriter("utf-8")

    inputreader = reader(input)
    outputwriter = writer(output)

    items = 0
    outputwriter.write("!Type:Bank\n")
    for row in unicode_csv_reader(inputreader.readlines(), delimiter=';'):
        if items == 0 and len(row) > 0 and row[0] == u"#Datum uskutečnění transakce":
            items = 1
            continue
        if items == 1:
            if len(row) == 0:
                break
            date = row[1]
            d, m, y = date.split('-')
            outputwriter.write(u"D%s/%s/%s\n" % (m, d, y))
            outputwriter.write(u"T%s\n" % row[9].replace(',','.'))
            trans_type = row[2].replace('\'','').replace('"','').strip()
            trans_desc = row[3].replace('\'','').replace('"','').strip()
            trans_target = row[4].replace('\'','').replace('"','').strip()
            trans_acc = row[5].replace('\'','').replace('"','').strip()
            outputwriter.write(u"M%s %s %s %s\n" %  (trans_type,
                                                        trans_desc,
                                                        trans_target,
                                                        trans_acc) )
            outputwriter.write(u'^\n')

