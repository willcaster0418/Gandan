#--*--coding:utf-8--*--
from gandan.GandanPub import *
import time
if __name__ == "__main__":
	_h = GandanPub("127.0.0.1", 8080)
	_cnt = 0
	while True:
		_list = [{'this_is_test':_cnt} for i in range(10)]
		for _l in _list:
			_h.pub(sys.argv[1], str(_l))
		print("send", _cnt)
		time.sleep(0.1)
		_cnt = _cnt + 1
	_h.close()
