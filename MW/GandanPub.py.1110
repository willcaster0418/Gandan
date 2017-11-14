import struct, sys
import socket
import re
from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class GandanPub:
	def __init__(self, ip, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip, port))
	def pub(self, _cmd, _data):
		GandanMsg.send(None, self.s, _cmd, _data)
	def close(self):
		self.s.close()
	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

if __name__ == "__main__":
	_h = GandanPub("127.0.0.1", 8888)
	_list = [str(a)+b+c+d+e+f+g+h+i+j for a in range(1,10)
					       for b in ['e', 'f', 'g']
					       for c in ['h', 'i', 'j']
					       for d in ['k', 'l', 'm']
					       for e in ['k', 'l', 'm']
					       for f in ['k', 'l', 'm']
					       for g in ['k', 'l', 'm']
					       for h in ['k', 'l', 'm']
					       for i in ['k', 'l', 'm']
					       for j in ['k', 'l', 'm', 'a', 'b', 'c', 'd', 'e']]
	for _l in _list:
		_h.pub(sys.argv[1], _l)
		print(_l)
		import random
		import time;time.sleep(random.random()*0.1)
	_h.close()
