from gandan import MMAP
import time
from datetime import datetime as dt
m = MMAP("/tmp/some.que", 32*1024, 32)
gap_total = 0
gap_count = 0
while True:
    datas = m.readp()
    for data in datas:
        data = str(data, 'ascii')
        cnt, tv = data.split("|")
        cnt, tv = int(cnt), float(tv)
        gap = (dt.now().timestamp() - tv)
        gap_total += gap; gap_count += 1
        if gap_count % 10 == 0:
            print(gap_total/gap_count)
