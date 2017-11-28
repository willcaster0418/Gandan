import struct, sys
import socket
import re
import threading, time
import logging

from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class GandanPub:
	def __init__(self, ip, port, replay = 0):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_port_ = (ip, port)
		self.s = GandanPub.connect(None, self.s, self.ip_port_)
		self.replay_ = replay
		self.buff = []
		self.cmd_ = None
		#for multiple use
		self.publock = threading.Lock()

	def hb(self):
		while True:
			try:
				self.publock.acquire()
				hb_msg = "HB"
				GandanMsg.send(None, self.s, self.cmd_, hb_msg)
				self.publock.release()
				logging.info("send HB for topic[%s]...done" % self.cmd_)
				time.sleep(30)
			except Exception as e:
				self.publock.release()
				continue

	def pub(self, _cmd, _data):
		try:
			if self.cmd_ == None:
				self.cmd_ = _cmd
				self.hb_thr = threading.Thread(target=self.hb, args=())
				self.hb_thr.start()
			try:
				self.publock.acquire()
				GandanMsg.send(None, self.s, _cmd, _data)
				self.publock.release()
			except Exception as e:
				logging.info(str(e))
				self.publock.release()
				raise Exception("connection lost")

		except Exception as e:
			logging.info(str(e))
			logging.info("connection lost retry ... ")
			if self.replay_ == 1:
				self.buff.append(_data)

			try:
				self.s.close()
				self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.s = GandanPub.connect(None, self.s, self.ip_port_)

			except Exception as e:
				logging.info(str(e))
				logging.info("connection buff[%s]" % str(self.buff))
				return

			if self.replay_ == 1:
				for _d in self.buff:
					self.pub(_cmd, _d)
			self.buff = []

	def close(self):
		self.s.close()

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

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
