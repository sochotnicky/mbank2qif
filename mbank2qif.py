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

if len(sys.argv) != 3:
    print "Usage: %s input_file.csv output_file.qif" % sys.argv[0]
    sys.exit(1)

with nested(open(sys.argv[1], 'r'), open(sys.argv[2], 'w')) as (input, output):
    reader = codecs.getreader("cp1250")
    writer = codecs.getwriter("utf-8")

    inputreader = reader(input)
    outputwriter = writer(output)

    items = 0
    outputwriter.write("!Type:Bank\n")
    for line in inputreader.readlines():
        if items == 0 and line.startswith(u"#Datum uskutečnění transakce;"):
            items = 1
            inputreader.readline()
            continue
        if items == 1:
            props = line.split(';')
            if len(props) == 1:
                break
            date = props[1]
            d, m, y = date.split('-')
            outputwriter.write(u"D%s/%s/%s\n" % (m, d, y))
            outputwriter.write(u"T%s\n" % props[6].replace(',','.'))
            outputwriter.write(u"M%s\n" % props[2][1:-1].strip())
            outputwriter.write(u'^\n')

