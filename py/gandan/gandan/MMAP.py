import os,struct,threading,time,gc,logging
from mmap import mmap
from .Gandan import * 

class MMAP:
	def __init__(self, path, size, item_size):
		self.f = self.init_file(path, size)
		self.f.seek(0, os.SEEK_SET); self.m = mmap(self.f.fileno(), 11+size)
		self.size	  = size
		self.item_size = item_size
		self.item_num  = int(size/item_size)
		self.erase_buff_ = ''
		for i in range(0, item_size):
			self.erase_buff_ += ' '
		self.erase_buff_ = bytes(self.erase_buff_, "ascii")
		self.m_lock = threading.Lock()

	def init_file(self, path, size):
		#import pdb; pdb.set_trace()
		if os.path.isfile(path):
			f = open(path, "rb+");f.seek(0, os.SEEK_END)
			filesize = f.tell() ;f.seek(0, os.SEEK_SET)

			if f.read(3).decode("ascii") == "QUE":
			   if filesize < 11 + size:
				   f.seek(filesize, os.SEEK_SET)
				   for i in range(filesize, 11 + size):
					   f.write(' '.encode("ascii"))
			   return f
		f = open(path, "wb+");
		f.seek(0, os.SEEK_SET)
		f.write("QUE".encode("ascii"))
		f.write(struct.pack("i", 0))
		f.write(struct.pack("i", 0))
		for i in range(0, 11 + size):
			f.write(' '.encode("ascii"))
		return f

	def r (self): return struct.unpack("i", self.m[3: 7])[0]
	def w (self): return struct.unpack("i", self.m[7:11])[0]
	def rp(self): self.m.seek(3, os.SEEK_SET); self.m.write(struct.pack("i", self.r()+1))
	def wp(self): self.m.seek(7, os.SEEK_SET); self.m.write(struct.pack("i", self.w()+1))
	def rs(self, r): self.m.seek(3, os.SEEK_SET); self.m.write(struct.pack("i", r))
	def ws(self, w): self.m.seek(7, os.SEEK_SET); self.m.write(struct.pack("i", w))

	def writep(self, data): 
		try:
			self.m_lock.acquire()
			#print("write lock")
			self.write(data); self.ws(self.w()+1); del(data); 
		except Exception as e:
			print(str(e))
		finally:
			self.m_lock.release()

		return self.r();

	def readp(self)	   : 
		try:
			self.m_lock.acquire()
			#print("read lock")
			_l = self.read(); self.rs(self.r() + len(_l)); 
		except Exception as e:
			print(str(e))
		finally:
			self.m_lock.release()
			return _l

	def write(self, data):
		write_pos = 11 + (self.w()*self.item_size) % self.size
		write_res = (write_pos - 11) % self.item_size
		#clear que item before write
		try:
			if write_res == 0 : 
				self.m.seek(write_pos, os.SEEK_SET); self.m.write(self.erase_buff_)
				self.m.seek(write_pos, os.SEEK_SET); self.m.write(data)
			else			  : 
				self.m.seek(write_pos, os.SEEK_SET); self.m.write(self.erase_buff_[0:write_res])
				self.m.seek(11       , os.SEEK_SET); self.m.write(self.erase_buff_[write_res: self.item_size])
				self.m.seek(write_pos, os.SEEK_SET); self.m.write(data[0: write_res])
				self.m.seek(11	     , os.SEEK_SET); self.m.write(data[write_res: self.item_size ])
		except Exception as e:
			logging.info("try to write ", write_pos, "@", self.size + 11)

	def read(self):
		try:
			_l = []
			for i in range(self.r(), self.w()):
				read_pos = 11 + (i*self.item_size) % self.size
				read_res = (read_pos - 11) % self.item_size
				try:
					if read_pos == 11 + self.size :
						_l.append(self.m[11:11+self.item_size])
					elif read_res == 0 : 
						_l.append(self.m[read_pos:read_pos + self.item_size])
					else			 :
						data = ""
						self.m.seek(read_pos, os.SEEK_SET); data = self.m.read(self.item_size - read_res)
						self.m.seek(11	  , os.SEEK_SET); data = data + self.m.read(read_res)
						_l.append(data)
				except Exception as e:
					logging.info("try to read", read_pos, "@", self.size + 11)
			return _l
		except Exception as e:
			logging.info(str(e))

class RoboMMAP(threading.Thread, MMAP):
	def __init__(self, path, topic, callback, size, item_size):
		threading.Thread.__init__(self)
		MMAP.__init__(self, path, size, item_size)
		self.topic	= topic
		self.time	= 0.001
		self.callback = callback

	def run (self)   : self.handle()

	def handle(self, flag=True):
		#put handler in while loop
		while True:
			try:
				#time.sleep(self.time)
				if self.r() < self.w() and self.callback != None:
					_list = self.readp()
					self.callback(self.topic, _list, self.r(), self.w())
				else:
					logging.info("nothing to read")

				if flag == False:
					for i in range(0, len(_list)):
						logging.info(_list[i].strip())
					break
			except Exception as e:
				logging.info("#Error:"+str(e))
				break
