from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

from P import *
import json

_id = 0

def callback(_h):
	global _id
	#print(_h.cmd_, str(_h.dat_).strip())
	s = str(_h.dat_).strip().replace('\'', '\"')
	if _id > 3:
		j = P("some", print, json.dumps(json.loads(s), indent=4))
	else:
		j = P(_id, print, json.dumps(json.loads(s), indent=4))
	_id += 1

if __name__ == "__main__":
	_h = GandanSub("127.0.0.1", 8889, sys.argv[1], 1)
	while True:
		_h.sub(callback)
