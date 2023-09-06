from gandan import MMAP
import time
from datetime import datetime as dt
import logging

logging.basicConfig(
    filename = f"/tmp/test_recv.log",
    format ='%(asctime)s:%(levelname)s:%(message)s',
    datefmt ='%m/%d/%Y %I:%M:%S %p',
    level = logging.INFO
)
        
m = MMAP("/tmp/some.que", 128*4096, 128)
gap_total = 0
gap_count = 0

validity_dict = {}

while True:
    datas = m.readp()
    for data in datas:
        data = str(data, 'ascii')
        id, cnt, tv = data.split("|")
        cnt, tv = int(cnt), float(tv)
        gap = (dt.now().timestamp() - tv)
        gap_total += gap; gap_count += 1
        # if gap_count % 10 == 0:
        # logging.error(gap_total/gap_count)
        #logging.error("%s-%d" % (id, cnt))
        if not id in validity_dict.keys():
            validity_dict[id] = cnt
        else:
            gap = cnt - validity_dict[id] 
            if gap != 1:
                logging.error("error occured in %s, %d, %d - %d" % (id, gap, cnt, validity_dict[id]))
            validity_dict[id] = cnt
