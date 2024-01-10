import os,struct,threading,time,gc,logging
from mmap import mmap
import fcntl
import datetime

class MMAP:
    (CNT_START, CNT_SIZE) = 3, 4
    (RSTAMP_START, RSTAMP_SIZE) = 7, 8
    (WSTAMP_START, WSTAMP_SIZE) = 15, 8
    (R_START, R_SIZE) = 23, 4
    (W_START, W_SIZE) = 27, 4
    OFFSET_START = 31

    def __init__(self, path, size, item_size, opt = []):
        (self.use_cnt, self.use_tstamp) = (0, 0)
        if "TSTAMP" in opt:
            self.use_tstamp = 1
        
        self.f = self.init_file(path, size)
        
        self.f.seek(0, os.SEEK_SET); self.m = mmap(self.f.fileno(), MMAP.OFFSET_START+size)
        self.countp()
        self.size      = size
        self.item_size = item_size
        self.item_num  = int(size/item_size)
        self.erase_buff_ = ''
        for i in range(0, item_size):
            self.erase_buff_ += ' '
        self.erase_buff_ = bytes(self.erase_buff_, "ascii")


    def init_file(self, path, size):
        if os.path.isfile(path):
            f = open(path, "rb+");f.seek(0, os.SEEK_END)
            filesize = f.tell() ;f.seek(0, os.SEEK_SET)

            if f.read(3).decode("ascii") == "QUE":
               if filesize < MMAP.OFFSET_START + size:
                   f.seek(filesize, os.SEEK_SET)
                   for i in range(filesize, MMAP.OFFSET_START+ size):
                       f.write(' '.encode("ascii"))
               return f
        f = open(path, "wb+");
        f.seek(0, os.SEEK_SET)
        f.write("QUE".encode("ascii"))

        f.seek(MMAP.CNT_START, os.SEEK_SET)
        f.write(struct.pack("i", 1))

        if self.use_tstamp:
            f.seek(MMAP.RSTAMP_START, os.SEEK_SET)
            f.write(struct.pack("d", 0.0))
            f.seek(MMAP.WSTAMP_START, os.SEEK_SET)
            f.write(struct.pack("d", 0.0))

        f.seek(MMAP.R_START, os.SEEK_SET)
        f.write(struct.pack("i", 0))
        f.seek(MMAP.W_START, os.SEEK_SET)
        f.write(struct.pack("i", 0))

        for i in range(0, MMAP.OFFSET_START + size):
            f.write(' '.encode("ascii"))
        return f

    def close(self):
        self.countm()
        self.m.close()
        self.f.close()

    def r (self): return struct.unpack("i", self.m[MMAP.R_START: MMAP.R_START + MMAP.R_SIZE])[0]
    def w (self): return struct.unpack("i", self.m[MMAP.W_START: MMAP.W_START + MMAP.W_SIZE])[0]
    def rp(self): self.m.seek(MMAP.R_START, os.SEEK_SET); self.m.write(struct.pack("i", self.r()+1))
    def wp(self): self.m.seek(MMAP.W_START, os.SEEK_SET); self.m.write(struct.pack("i", self.w()+1))
    def rs(self, r): self.m.seek(MMAP.R_START, os.SEEK_SET); self.m.write(struct.pack("i", r))
    def ws(self, w): self.m.seek(MMAP.W_START, os.SEEK_SET); self.m.write(struct.pack("i", w))
    def rstamp(self): return struct.unpack("d", self.m[MMAP.RSTAMP_START: MMAP.RSTAMP_START + MMAP.RSTAMP_SIZE])[0]
    def wstamp(self): return struct.unpack("d", self.m[MMAP.WSTAMP_START: MMAP.WSTAMP_START + MMAP.WSTAMP_SIZE])[0]
    def count(self):  return struct.unpack("i", self.m[MMAP.CNT_START: MMAP.CNT_START + MMAP.CNT_SIZE])[0]

    def countp(self): 
        while fcntl.flock(self.f, fcntl.LOCK_EX) == False:
            time.sleep(0.0001)
            continue
        try:
            self.m.seek(MMAP.CNT_START, os.SEEK_SET); self.m.write(struct.pack("i", self.count() + 1))
        except Exception as e:
            print(str(e))
        finally:
            fcntl.flock(self.f, fcntl.LOCK_UN)

    def countm(self): 
        while fcntl.flock(self.f, fcntl.LOCK_EX) == False:
            time.sleep(0.0001)
            continue
        try:
            self.m.seek(MMAP.CNT_START, os.SEEK_SET); self.m.write(struct.pack("i", self.count() - 1))
        except Exception as e:
            print(str(e))
        finally:
            fcntl.flock(self.f, fcntl.LOCK_UN)

    def writep(self, data): 
        while fcntl.flock(self.f, fcntl.LOCK_EX) == False:
            time.sleep(0.0001)
            continue
        try:
            self.write(data); self.ws(self.w()+1); del(data); 
            if self.use_tstamp:
                self.m.seek(MMAP.WSTAMP_START, os.SEEK_SET)
                self.m.write(struct.pack('d', datetime.datetime.now().timestamp()))
        except Exception as e:
            print(str(e))
        finally:
            fcntl.flock(self.f, fcntl.LOCK_UN)

        return self.r();

    def readp(self)       : 
        while fcntl.flock(self.f, fcntl.LOCK_EX) == False:
            time.sleep(0.0001)
            continue
        try:
            _l = self.read(); self.rs(self.r() + len(_l)); 
            if self.use_tstamp:
                self.m.seek(MMAP.RSTAMP_START, os.SEEK_SET)
                self.m.write(struct.pack('d', datetime.datetime.now().timestamp()))
        except Exception as e:
            print(str(e))
        finally:
            fcntl.flock(self.f, fcntl.LOCK_UN)
            return _l

    def write(self, data):
        write_pos = MMAP.OFFSET_START + (self.w()*self.item_size) % self.size
        write_res = (write_pos - MMAP.OFFSET_START) % self.item_size
        #clear que item before write
        try:
            if write_res == 0 : 
                self.m.seek(write_pos, os.SEEK_SET); self.m.write(self.erase_buff_)
                self.m.seek(write_pos, os.SEEK_SET); self.m.write(data)
            else              : 
                self.m.seek(write_pos, os.SEEK_SET); self.m.write(self.erase_buff_[0:write_res])
                self.m.seek(MMAP.OFFSET_START, os.SEEK_SET); self.m.write(self.erase_buff_[write_res: self.item_size])
                self.m.seek(write_pos, os.SEEK_SET); self.m.write(data[0: write_res])
                self.m.seek(MMAP.OFFSET_START, os.SEEK_SET); self.m.write(data[write_res: self.item_size ])
        except Exception as e:
            logging.info("try to write ", write_pos, "@", self.size + 11)

    def read(self):
        try:
            _l = []
            for i in range(self.r(), self.w()):
                read_pos = MMAP.OFFSET_START + (i*self.item_size) % self.size
                read_res = (read_pos - MMAP.OFFSET_START) % self.item_size
                try:
                    if read_pos == MMAP.OFFSET_START + self.size :
                        _l.append(self.m[MMAP.OFFSET_START:MMAP.OFFSET_START+self.item_size])
                    elif read_res == 0 : 
                        _l.append(self.m[read_pos:read_pos + self.item_size])
                    else             :
                        data = ""
                        self.m.seek(read_pos, os.SEEK_SET); data = self.m.read(self.item_size - read_res)
                        self.m.seek(MMAP.OFFSET_START, os.SEEK_SET); data = data + self.m.read(read_res)
                        _l.append(data)
                except Exception as e:
                    logging.info("try to read", read_pos, "@", self.size + MMAP.OFFSET_START)
            return _l
        except Exception as e:
            logging.info(str(e))

class RoboMMAP(threading.Thread, MMAP):
    def __init__(self, path, topic, callback, size, item_size):
        threading.Thread.__init__(self)
        MMAP.__init__(self, path, size, item_size)
        self.topic    = topic
        self.time    = 0.0001
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
