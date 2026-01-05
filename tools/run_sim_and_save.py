from utils import simular
from utils.data_manager import reset_db, save_batch

# 1. Reset DB local CSVs
print('Resetting DB...')
reset_db()

# 2. Generate 12 months of coherent simulation
print('Generating simulation (12 months)...')
data, metas = simular(n=0, months=12)

# 3. Save to CSV/Sheets via save_batch
print('Saving batch...')
save_batch(data)

print('Done.')
