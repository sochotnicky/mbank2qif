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
import csv
import argparse

class TransactionData(object):
    """Simple class to hold information about a transaction"""
    def __init__(self, date, amount, destination=None, message=None):
        self.date = date
        self.amount = amount
        self.destination = destination
        self.message = message

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

def convert(infile, outfile):
    with nested(open(infile, 'r'), open(outfile, 'w')) as (input, output):
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

def write_qif(outfile, transactions):
    with open(outfile, 'w') as output:
        writer = codecs.getwriter("utf-8")
        outputwriter = writer(output)
        outputwriter.write("!Type:Bank\n")
        for transaction in transactions:
            d, m, y = transaction.date.day,\
                      transaction.date.monty,\
                      transaction.date.year
            outputwriter.write(u"D%s/%s/%s\n" % (m, d, y))
            outputwriter.write(u"T%s\n" % transaction.amount)
            outputwriter.write(u"M%s\n" % transaction.message)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bank statement to QIF file converter')
    parser.add_argument('-i', '--input',
                        help='input file to process [default:stdin]',
                        default='/dev/stdin')
    parser.add_argument('-o', '--output',
                        help='output file [default:stdout]',
                        default='/dev/stdout')
    parser.add_argument('-t', '--type',
                        help='Type of input file [default:mbank]',
                        default='mbank')
    args = parser.parse_args()
    convert(args.input, args.output)

