import struct, sys, time, re
from ast import literal_eval
from datetime import datetime
import socket
import threading, logging

from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

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
		l_format = '%(asctime)s^%(levelname)s^%(message)s'
		d_format = '%Y-%m-%d^%H:%M:%S'
		logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=logging.DEBUG)

	def log(self, _d):
		logging.info(_d)

	def handler(self, _req):
		_p = None
		while(True):
			try:	
				_h = GandanMsg.recv(None, _req)
				if Gandan.version(None) < 300:
					self.log(_h.__str__())
					print(_h.__str__())
				else:
					self.log(str(_h))
				if _h == None: break
				(_cmd, _msg) = (_h.cmd_, _h.dat_)
				_p = self.pubsub(_p, _req, _cmd, _msg)
			except Exception as e:
				self.log("handler %s" % str(e))
				break
		self.log("handler for %s is done" % str(_req))

	def pubsub(self, _pub, _req, _t, _msg):
		[_cmd, _topic]  = _t.split("_")
		_path = self.path_+_topic
		if _cmd == "PUB" and _topic in self.pub_topic_.keys(): 
			self.log("PUB write %s, " % _topic + "%s" % _msg)
			if _pub == None:
				_pub = RoboMMAP(_path, _topic, self.mon, self.sz_, self.isz_)
				_pub.start()
			if Gandan.version(None) < 300:
				_pub.writep(bytes(_msg))
			else:
				_pub.writep(bytes(_msg,'utf-8'))
		elif _cmd == "PUB":
			self.pub_topic_[_topic] = []
			self.pub_topic_[_topic].append(RoboMMAP(_path, _topic, self.mon, self.sz_, self.isz_))
			self.pub_topic_[_topic][-1].start()
			_pub = self.pub_topic_[_topic][-1]
			self.log("PUB que path : %s monitor start" % _path + ", TOPIC : %s" % _topic)
		elif _cmd == "SUB" and not _topic in self.sub_topic_.keys():
			self.sub_topic_[_topic] = []
			self.sub_topic_[_topic].append(_req)
			self.log("_cmd : %s" % _cmd + "_topic : %s is created for SUB" % _topic)
		elif _cmd == "SUB":
			self.sub_topic_[_topic].append(_req)
			self.log("_cmd : %s" % _cmd + "_topic : %s is appended for SUB" % _topic)
		else:
			self.log("%s, " % _cmd + "%s" % _topic)
		return _pub

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
			try:
				for d in _data:
					if Gandan.version(None) < 300:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d))
					else:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d,'utf-8'))
			except Exception as e:
				self.log("%s"%str(e)+":%s"%str(e))
				continue
	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8888)
		h = Gandan(l_ip_port, "/home/robosys/Gandan/MW/que/", 10000, 500)
		h.setup_log(datetime.now().strftime("/home/robosys/Gandan/MW/log/%Y%m%d")+".Gandan.log")
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

