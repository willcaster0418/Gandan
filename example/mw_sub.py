from gandan.MMAP import *
from gandan.Gandan import *
from gandan.GandanMsg import *
from gandan.GandanPub import *
from gandan.GandanSub import *

import json

def callback(_h):
	print("RECV:"+str(_h.dat_).strip())
	return

if __name__ == "__main__":
	_h = GandanSub("127.0.0.1", 8889, sys.argv[1], 0.1)
	while True:
		_h.sub(callback)
