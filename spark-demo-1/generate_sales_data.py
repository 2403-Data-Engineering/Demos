import csv
import random
import os
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION — tweak these values to adjust the output
# ============================================================

NUM_ROWS = 1500
ERROR_RATE = 0.05          # 0.05 = 5% of rows will have errors
RANDOM_SEED = 42           # Change for different random output
DATE_START = '2024-01-01'
DATE_END = '2024-12-31'
WEEKDAY_WEIGHT = 5         # How much more likely weekdays are vs weekends
WEEKEND_WEIGHT = 1
OUTPUT_FILENAME = 'sales_data.csv'

# Store volume: high-traffic, low-traffic, or default (3)
STORE_WEIGHTS = {
    'STR-011': 5,  # New York Midtown — high
    'STR-004': 5,  # Chicago Loop — high
    'STR-009': 5,  # Houston Galleria — high
    'STR-005': 1,  # Minneapolis North — low
    'STR-006': 1,  # Columbus Square — low
}
DEFAULT_STORE_WEIGHT = 3

# Product frequency: high sellers, low sellers, default (3)
HIGH_FREQ_PRODUCTS = {'PRD-012', 'PRD-013', 'PRD-035', 'PRD-036', 'PRD-041',
                      'PRD-022', 'PRD-023', 'PRD-044', 'PRD-008', 'PRD-015'}
LOW_FREQ_PRODUCTS = {'PRD-025', 'PRD-026', 'PRD-027', 'PRD-028', 'PRD-029',
                     'PRD-030', 'PRD-031', 'PRD-032', 'PRD-033', 'PRD-034'}
HIGH_FREQ_WEIGHT = 6
LOW_FREQ_WEIGHT = 1
DEFAULT_PRODUCT_WEIGHT = 3

# Quantity ranges by category
QUANTITY_RANGES = {
    'Office Supplies': (1, 20),
    'Breakroom': (1, 15),
    'Electronics': (1, 5),
    'Software': (1, 5),
    'Furniture': (1, 2),
}

# Error type distribution (relative proportions)
ERROR_MIX = {
    'missing_product_id': 15,
    'missing_store_id': 15,
    'invalid_quantity': 15,
    'orphan_product_id': 10,
    'duplicate_txn_id': 10,
    'malformed_row': 10,
}

# ============================================================
# SCRIPT — no need to edit below this line
# ============================================================

random.seed(RANDOM_SEED)

# Resolve paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load lookup tables ---

def load_csv(filename):
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

stores = load_csv('stores.csv')
products = load_csv('products.csv')

store_ids = [s['store_id'] for s in stores]
product_lookup = {p['product_id']: p for p in products}
product_ids = list(product_lookup.keys())

# --- Weighting: stores ---

store_pool = []
for sid in store_ids:
    weight = STORE_WEIGHTS.get(sid, DEFAULT_STORE_WEIGHT)
    store_pool.extend([sid] * weight)

# --- Weighting: products ---

product_pool = []
for pid in product_ids:
    if pid in HIGH_FREQ_PRODUCTS:
        product_pool.extend([pid] * HIGH_FREQ_WEIGHT)
    elif pid in LOW_FREQ_PRODUCTS:
        product_pool.extend([pid] * LOW_FREQ_WEIGHT)
    else:
        product_pool.extend([pid] * DEFAULT_PRODUCT_WEIGHT)

# --- Date generation ---

start_date = datetime.strptime(DATE_START, '%Y-%m-%d')
end_date = datetime.strptime(DATE_END, '%Y-%m-%d')
all_days = []
d = start_date
while d <= end_date:
    weight = WEEKDAY_WEIGHT if d.weekday() < 5 else WEEKEND_WEIGHT
    all_days.extend([d] * weight)
    d += timedelta(days=1)

# --- Error distribution ---

error_distribution = []
for error_type, count in ERROR_MIX.items():
    error_distribution.extend([error_type] * count)

# --- Generate rows ---

NUM_ROWS = 1500
ERROR_RATE = 0.05

rows = []
used_txn_ids = []
error_count = 0
target_errors = int(NUM_ROWS * ERROR_RATE)

for i in range(NUM_ROWS):
    txn_id = f"TXN-{i+1:05d}"
    date = random.choice(all_days).strftime('%Y-%m-%d')
    store_id = random.choice(store_pool)
    product_id = random.choice(product_pool)
    product = product_lookup[product_id]
    category = product['category']
    qty_min, qty_max = QUANTITY_RANGES[category]
    quantity = random.randint(qty_min, qty_max)
    unit_price = float(product['unit_cost'])
    total = round(quantity * unit_price, 2)

    # Decide if this row gets an error
    if error_count < target_errors and random.random() < ERROR_RATE:
        error_type = random.choice(error_distribution)
        error_count += 1

        if error_type == 'missing_product_id':
            rows.append([txn_id, date, store_id, '', quantity, unit_price, total])
        elif error_type == 'missing_store_id':
            rows.append([txn_id, date, '', product_id, quantity, unit_price, total])
        elif error_type == 'invalid_quantity':
            bad_qty = random.choice([-1, -2, 0])
            rows.append([txn_id, date, store_id, product_id, bad_qty, unit_price, round(bad_qty * unit_price, 2)])
        elif error_type == 'orphan_product_id':
            rows.append([txn_id, date, store_id, 'PRD-999', quantity, 0.00, 0.00])
        elif error_type == 'duplicate_txn_id' and used_txn_ids:
            dup_id = random.choice(used_txn_ids)
            rows.append([dup_id, date, store_id, product_id, quantity, unit_price, total])
        elif error_type == 'malformed_row':
            # Extra comma creates an extra field
            rows.append([txn_id, date, store_id, product_id, quantity, unit_price, total, 'EXTRA_FIELD'])
        else:
            # Fallback to clean row
            rows.append([txn_id, date, store_id, product_id, quantity, unit_price, total])
    else:
        rows.append([txn_id, date, store_id, product_id, quantity, unit_price, total])

    used_txn_ids.append(txn_id)

# Shuffle so errors aren't clustered
random.shuffle(rows)

# --- Write output ---

output_path = os.path.join(SCRIPT_DIR, OUTPUT_FILENAME)
with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['transaction_id', 'date', 'store_id', 'product_id', 'quantity', 'unit_price', 'total'])
    for row in rows:
        writer.writerow(row)

# --- Summary ---

malformed = sum(1 for r in rows if len(r) != 7)
missing_prod = sum(1 for r in rows if len(r) == 7 and r[3] == '')
missing_store = sum(1 for r in rows if len(r) == 7 and r[2] == '')
invalid_qty = sum(1 for r in rows if len(r) == 7 and isinstance(r[4], int) and r[4] <= 0)
orphan = sum(1 for r in rows if len(r) == 7 and r[3] == 'PRD-999')

print(f"Generated {len(rows)} rows")
print(f"Errors injected: ~{error_count}")
print(f"  Malformed rows: {malformed}")
print(f"  Missing product_id: {missing_prod}")
print(f"  Missing store_id: {missing_store}")
print(f"  Invalid quantity: {invalid_qty}")
print(f"  Orphan product_id: {orphan}")
print(f"  (Duplicate txn_ids not counted here — check manually)")
print(f"\nOutput: {OUTPUT_FILENAME}")