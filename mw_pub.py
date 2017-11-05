from MW.GandanPub import *

if __name__ == "__main__":
	_h = GandanPub("127.0.0.1", 8888)
	_list = [{'seq' : 0, 'code':code, 'side':sb, 'price':price, 'qty':qty,
			  'prev_no' : 0, 'order_type':otype, 'price_type':ptype}
				for code  in ['005930', '079430']
				for sb    in ['S', 'B']
				for ptype in ['M']
				for otype in ['N']
				for price in range(0, 1)
				for qty   in range(1, 2)]
	while True:
		for _l in _list:
			_h.pub(sys.argv[1], str(_l))
			import time;time.sleep(5)

	_h.close()
