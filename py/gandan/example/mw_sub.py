from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

import json

def callback(_h):
	print("RECV:"+str(_h.dat_).strip())
	return

if __name__ == "__main__":
	_h = GandanSub("127.0.0.1", 8889, sys.argv[1], 0.1)
	while True:
		try:
			_h.sub(callback)
		except Exception as e:
			continue
