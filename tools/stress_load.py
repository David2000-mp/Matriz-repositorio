import time
from utils import data_manager as dm

n = 100
start = time.time()
for i in range(n):
    dm.load_data()
    if (i+1) % 20 == 0:
        print(f"iter {i+1}")
end = time.time()
print('total_seconds:', end - start)
