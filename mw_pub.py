from MW.GandanPub import *

if __name__ == "__main__":
	_h = GandanPub("127.0.0.1", 8889)
	_list = [{'a':1}, {'b':1}, {'c':1}]
	while True:
		for _l in _list:
			_h.pub(sys.argv[1], str(_l))
			import time;time.sleep(1)

	_h.close()
