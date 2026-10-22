"""Write small partitioned CSVs: sample_data/orders/dt=YYYY-MM-DD/part-0.csv (Hive-style partitions)."""
import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path


def generate(out_dir: str = "labs/lab05_glue_athena/sample_data", days: int = 7, rows_per_day: int = 200, seed: int = 1) -> int:
    rnd = random.Random(seed)
    start = date(2026, 1, 1)
    total = 0
    for d in range(days):
        day = start + timedelta(days=d)
        part = Path(out_dir) / "orders" / f"dt={day.isoformat()}"
        part.mkdir(parents=True, exist_ok=True)
        with open(part / "part-0.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["order_id", "customer_id", "amount", "status"])  # dt comes from the folder name, not the file
            for i in range(rows_per_day):
                w.writerow([f"{day:%m%d}-{i:04d}", f"C{rnd.randint(1, 50):03d}", round(rnd.uniform(5, 500), 2),
                            rnd.choices(["PLACED", "SHIPPED", "CANCELLED"], [6, 3, 1])[0]])
                total += 1
    return total


if __name__ == "__main__":
    print(generate(*(sys.argv[1:2] or [])), "rows written")
