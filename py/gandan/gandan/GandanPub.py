#--*--encoding:utf-8--*--
import struct, sys
import socket
import re
import threading, time
import logging

try:
	from .GandanMsg import *
	from .MMAP  import *
except Exception as e:
	from GandanMsg import *
	from MMAP  import *
	

class GandanPub:
	def __init__(self, ip, port, path=None):
		if path == None:
			self.type_ = 0
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ip_port_ = (ip, port)
			self.s = GandanPub.connect(None, self.s, self.ip_port_)
			self.prev_cmd_ = None
			self.prev_data_ = None
			self.cmd_ = None
		else:
			self.type_ = 1
			self.mmap = None
			self.path = path

	def pub_shm(self, _cmd, _data):
		if self.mmap == None:
			size = 5000*20000
			item_size = 20000
			self.topic = _cmd.split('_')[1]
			self.mmap = MMAP(self.path+"/"+self.topic, size, item_size)
		else:
			self.mmap.writep(bytes(_data, 'utf-8'))
		
	def pub(self, _cmd, _data):
		if self.type_ == 0:
			if self.cmd_ == None:
				self.cmd_ = _cmd
			try:
				GandanMsg.send(None, self.s, _cmd, _data)
			except Exception as e:
				logging.info(str(e))
				raise Exception("connection lost")

		elif self.type_ == 1:
			self.pub_shm(_cmd, _data)

	def close(self):
		if self.type_ == 0:
			self.s.close()
			self.hb_flag = False
		elif self.type_ == 1:
			self.mmap.f.close()

	@staticmethod
	def connect(self, _sock, _ip_port):
		_sock.connect(_ip_port)
		return _sock

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
