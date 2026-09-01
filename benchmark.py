import time
import tracemalloc
from collections import Counter
import multiprocessing as mp
import polars as pl

LOG_FILE = "server.log"

def measure_performance(func, name: str):
    tracemalloc.start()
    start_time = time.time()
    
    result = func()
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    duration = end_time - start_time
    peak_mb = peak / (1024 * 1024)
    
    print(f"[{name}] Done in {duration:.2f}s | Peak Memory: {peak_mb:.2f} MB")
    return result, duration, peak_mb

# (a) Naif Satır Döngüsü (Tüm satırları RAM'e yükler)
def approach_naive():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    counts = Counter()
    for line in lines:
        if "/api/v1/orders" in line:
            counts["orders"] += 1
    return counts

# (b) Generator + Counter (Bellek dostu akış)
def approach_generator():
    counts = Counter()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "/api/v1/orders" in line:
                counts["orders"] += 1
    return counts

# (c) Multiprocessing Chunk (Paralel İşleme)
def process_chunk(chunk_lines):
    count = 0
    for line in chunk_lines:
        if "/api/v1/orders" in line:
            count += 1
    return count

def approach_multiprocessing():
    chunk_size = 500_000
    total_orders = 0
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        while True:
            chunk = [f.readline() for _ in range(chunk_size)]
            if not chunk[0]:
                break
            with mp.Pool() as pool:
                results = pool.map(process_chunk, [chunk])
                total_orders += sum(results)
    return total_orders

# (d) Polars (Rust tabanlı vektörel işlem)
def approach_polars():
    # Metin dosyalarını satır satır okumak için en güvenli Polars yöntemi
    df = pl.scan_csv(LOG_FILE, has_header=False, separator="\x00", infer_schema_length=0)
    result = df.filter(pl.col("column_1").str.contains("/api/v1/orders")).select(pl.count()).collect()
    return result.item(0, 0)

if __name__ == "__main__":
    print("Starting Performance Benchmark...")
    
    print("\n--- Running Approach A (Naive) ---")
    _, t_naive, m_naive = measure_performance(approach_naive, "Naive Loop")
    
    print("\n--- Running Approach B (Generator) ---")
    _, t_gen, m_gen = measure_performance(approach_generator, "Generator")
    
    print("\n--- Running Approach C (Multiprocessing) ---")
    _, t_mp, m_mp = measure_performance(approach_multiprocessing, "Multiprocessing")
    
    print("\n--- Running Approach D (Polars) ---")
    _, t_pl, m_pl = measure_performance(approach_polars, "Polars")