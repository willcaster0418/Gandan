#--*--encoding:utf-8--*--
import struct, sys
import socket
import re
import threading, time
import logging

from .GandanMsg import *
from .MMAP  import *

class GandanPub:
	def __init__(self, ip, port, path=None, hb_time = 30):
		if path == None:
			self.type_ = 0
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ip_port_ = (ip, port)
			self.s = GandanPub.connect(None, self.s, self.ip_port_)
			self.prev_cmd_ = None
			self.prev_data_ = None
			self.cmd_ = None
			#for multiple use
			self.publock = threading.Lock()
			self.hb_flag = True
			self.hb_time = hb_time
		else:
			self.type_ = 1
			self.mmap = None
			self.path = path
		
	def hb(self, obj):
		while obj.hb_flag:
			try:
				self.pub(self.cmd_, "HB")
				#logging.info("-------------------HB-----------------[%s, %s]...done" % (self.cmd_, self.hb_flag))
				time.sleep(self.hb_time)
			except Exception as e:
				time.sleep(1)
				continue

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
				except Exception as e:
					logging.info(str(e))
					raise Exception("connection lost")
				finally:
					self.publock.release()

			except Exception as e:
				#while True:
				#	try:
				#		self.publock.acquire()
				#		logging.info("connection lost retry ... ")
				#		self.s.close()
				#		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				#		self.s = GandanPub.connect(None, self.s, self.ip_port_)
				#		logging.info("connection lost retry ... SUCC ")

				#		if False:#self.prev_cmd_ != None and self.prev_data_ != None:
				#			self.pub(self.prev_cmd_, self.prev_data_)
				#			logging.info("send[%s][%s] .. Done" % (self.prev_cmd_, self.prev_data_))

				#		for i in range(0, 10):
				#			self.pub(_cmd, "Re-Initialize Connection")
				#			time.sleep(0.1)

				#		self.pub(_cmd, _data)
				#		logging.info("send[%s][%s] .. Done" % (_cmd, _data))
				#		return 0

				#	except Exception as e:
				#		time.sleep(1)
				#	finally:
				#		self.publock.release()
				return 0
		elif self.type_ == 1:
			self.pub_shm(_cmd, _data)

	def close(self):
		if self.type_ == 0:
			self.s.close()
			self.hb_flag = False
		elif self.type_ == 1:
			self.mmap.f.close()
			self.hb_flag = False

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
