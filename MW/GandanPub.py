#--*--encoding:utf-8--*--
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
	def __init__(self, ip, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_port_ = (ip, port)
		self.s = GandanPub.connect(None, self.s, self.ip_port_)
		self.prev_cmd_ = None
		self.prev_data_ = None
		self.cmd_ = None
		#for multiple use
		self.publock = threading.Lock()
		self.hb_flag = True

	def hb(self, obj):
		while obj.hb_flag:
			try:
				#self.publock.acquire()
				hb_msg = "HB"
				#GandanMsg.send(None, self.s, self.cmd_, hb_msg)
				self.pub(self.cmd_, "HB")
				#self.publock.release()
				logging.info("send HB for topic[%s, %s]...done" % (self.cmd_, self.hb_flag))
				time.sleep(30)
			except Exception as e:
				#self.publock.release()
				time.sleep(1)
				continue

	def pub(self, _cmd, _data):
		try:
			if self.cmd_ == None:
				self.cmd_ = _cmd
				self.hb_thr = threading.Thread(target=self.hb, args=(self,))
				self.hb_thr.start()
			try:
				self.publock.acquire()
				GandanMsg.send(None, self.s, _cmd, _data)
				#socket closing 없이 죽은 경우, 첫번째 전송까지는 Exception 발생하지 않음
				#적절한 수준의 전송보장은 아닌 것 같음
				self.prev_cmd_ = _cmd
				self.prev_data_ = _data
				self.publock.release()
			except Exception as e:
				logging.info(str(e))
				self.publock.release()
				raise Exception("connection lost")

		except Exception as e:

			while True:
				try:
					logging.info("connection lost retry ... ")
					self.publock.acquire()
					self.s.close()
					self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self.s = GandanPub.connect(None, self.s, self.ip_port_)
					self.publock.release()
					logging.info("connection lost retry ... SUCC ")

					if False:#self.prev_cmd_ != None and self.prev_data_ != None:
						self.pub(self.prev_cmd_, self.prev_data_)
						logging.info("send[%s][%s] .. Done" % (self.prev_cmd_, self.prev_data_))

					for i in range(0, 10):
						self.pub(_cmd, "Re-Initialize Connection")
						time.sleep(0.1)

					self.pub(_cmd, _data)
					logging.info("send[%s][%s] .. Done" % (_cmd, _data))
					return 0

				except Exception as e:
					self.publock.release()
					time.sleep(1)

			return 0

	def close(self):
		self.s.close()
		self.hb_flag = False

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))

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
