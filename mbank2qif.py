
import codecs
import sys

input = open(sys.argv[1], "r")
reader = codecs.getreader("cp1250");

inputreader = reader(input)

print inputreader.read()
