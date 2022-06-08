from MW.MMAP import *
import sys
m = MMAP("./TEST", 10000, 100)

m.writep(bytes("testrrrrrcdcd", "utf-8"))
m.writep(bytes("testrrrrrcdcd", "utf-8"))
m.writep(bytes("testrrrrrcdcd", "utf-8"))

#result = m.readp()
#print(result)
