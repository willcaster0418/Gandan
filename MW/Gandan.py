#--*--coding=utf-8--*--
import struct, sys, time, re
from ast import literal_eval
from datetime import datetime
import socket
import threading, logging
import traceback

from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

from P import *

class Gandan:
	def __init__(self, ip_port, path, size, item_size):
		self.ip_port = ip_port
		self.path_ = path
		self.sz_   = size
		self.isz_  = item_size
		self.pub_topic_ = {}
		self.sub_topic_ = {}
		self.rlist_ = []

	def setup_log(self, path):
		l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(funcName)s^%(lineno)d^%(message)s'
		d_format = '%Y-%m-%d^%H:%M:%S'
		logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=logging.DEBUG)

	def log(self, _d):
		logging.info(_d)

	def handler(self, _req):
		_p = None
		_cnt_none = 0
		while(True):
			try:
				_h = GandanMsg.recv(None, _req)
			except Exception as e:
				continue

			try:	
				if _h == None: 
					#self.log("None is return from socket : %s" % str(_req))
					#SUB이 받으면 None을 return하는 경우가 종종 있는 거 같음
					if _cnt_none < 30:
						_cnt_none += 1
						continue
					else:
						break
				else:
					_cnt_none = 0
					self.log(_h.__str__())
					
				(_cmd, _msg) = (_h.cmd_, _h.dat_)
				[_pubsub, _topic]  = _cmd.split("_")
				if _pubsub == "PUB":
					self.log("PUB received with TOPIC[%s]" % _topic)
					_p = self.pub(_req, _topic, _msg)
				elif _pubsub == "SUB":
					self.log("SUB received with TOPIC[%s]" % _topic)
					_p = self.sub(_req, _topic, _msg)
				else:
					self.log("neither PUB nor SUB")
				del(_msg)
			except Exception as e:
				_type, _value, _traceback = sys.exc_info()
				#self.log("#Error" + str(_type) + str(_value) + str(traceback.format_tb(_traceback)))
				break
		self.log("handler is done socket : %s" % str(_req))

	def pub(self, _req, _topic, _msg):
		if (_topic == "ORDER" or _topic == "OM") and _req.getsockname()[0] != '127.0.0.1':
			raise Exception("Invalid Access to PUB ORDER or OM from %s" % _req.get_sockname()[0])
			_req.close()

		_path = self.path_+_topic

		if _topic in self.pub_topic_.keys(): 
			#self.log("PUB write %s, " % _topic + "%s" % _msg)
			_pub = self.pub_topic_[_topic][-1]
			_pub.writep(bytes(_msg,'utf-8'))
		else:
			self.pub_topic_[_topic] = []
			self.pub_topic_[_topic].append(RoboMMAP(_path, _topic, self.mon, self.sz_, self.isz_))
			self.pub_topic_[_topic][-1].start()
			_pub = self.pub_topic_[_topic][-1]
			_pub.writep(bytes(_msg,'utf-8'))
			self.log("PUB que path : %s monitor start" % _path + ", TOPIC : %s" % _topic)

	def sub(self, _req, _topic, _msg):
		if not _topic in self.sub_topic_.keys():
			self.sub_topic_[_topic] = []
			self.sub_topic_[_topic].append(_req)
			self.log("_topic : %s is created for SUB" % _topic)
		else:
			self.sub_topic_[_topic].append(_req)
			self.log("_topic : %s is appended for SUB" % _topic)

	def start(self):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind(self.ip_port)
			s.listen(10)
			while True:
				try:
					_r, _a = s.accept()
					self.rlist_.append(_r)
					t = threading.Thread(target = self.handler, args = (_r, ))
					t.start()
				except Exception as e:
					self.log("%s"%str(e)+":%s"%str(e))
					break

	def mon(self, _topic, _data):
		if not _topic in self.sub_topic_.keys():
			return
		for i, _req in enumerate(self.sub_topic_[_topic]):
			#self.log("SUB[%s] send to [%s]" % (_topic, str(_req)))
			try:
				for d in _data:
					if Gandan.version(None) < 300:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d))
					else:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d,'utf-8'))
			except Exception as e:
				self.log("#Error in SUB [%s]" % _topic)
				continue

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8888)
		h = Gandan(l_ip_port, "/home/robosys/Gandan/MW/que/", 10000, 1000)
		h.setup_log(datetime.now().strftime("/home/robosys/Gandan/MW/log/%Y%m%d")+".Gandan.log")
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

