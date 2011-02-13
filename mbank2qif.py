# -*- coding: utf-8 -*-

import codecs
import sys

input = open(sys.argv[1], "r")
output = open(sys.argv[2], "w")
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

