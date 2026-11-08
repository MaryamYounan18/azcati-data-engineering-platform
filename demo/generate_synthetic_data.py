"""
Generates two synthetic sensor CSV files in demo/data/:
  clean_data_{R}.csv   — standard column layout
  flagged_data_{R}.csv — has a "QC_Pass" Yes/No column inserted between
                         Conductivity and Dissolved Oxygen

Run once before run_demo.py to populate demo/data/.
"""
import csv, math, os, random
from datetime import datetime, timedelta

SENSORS_CLEAN   = ["timestamp", "reactor_id", "pH", "ORP", "temperature",
                   "conductivity", "dissolved_oxygen", "oxygen_saturation", "salinity"]
SENSORS_FLAGGED = ["timestamp", "reactor_id", "pH", "ORP", "temperature",
                   "conductivity", "QC_Pass",
                   "dissolved_oxygen", "oxygen_saturation", "salinity"]

START    = datetime(2024, 6, 1, 6, 0)
INTERVAL = timedelta(minutes=15)
N_DAYS   = 30
REACTORS = ["R1", "R2"]

random.seed(42)

def generate_rows(reactor_id, include_faults=False):
    rows, t = [], START
    for step in range(N_DAYS * 96):
        day_num  = step // 96
        day_frac = (step % 96) / 96
        sin_d    = math.sin(2 * math.pi * day_frac - math.pi / 2)

        ph   = round(7.5 + 0.4 * sin_d + random.gauss(0, 0.05), 2)
        orp  = round(220 + 30 * sin_d  + random.gauss(0, 5),    1)
        temp = round(30  + 3  * math.sin(2 * math.pi * (day_frac - 0.1)) + random.gauss(0, 0.3), 2)
        cond = round(15  + random.gauss(0, 0.5), 2)
        do_  = round(8   + 2  * sin_d  + random.gauss(0, 0.3),  2)
        sat  = round(90  + 10 * sin_d  + random.gauss(0, 2),    2)
        sal  = round(0.5 + random.gauss(0, 0.02), 3)

        if include_faults and reactor_id == "R1":
            if 10 <= day_num <= 12:          # stuck sensor at max
                sat, do_ = 500.0, 42.0
            if day_num == 15 and 0.4 < day_frac < 0.42:  # brief probe removal
                sat, do_ = 0.1, 0.0

        # 2-day maintenance gap on R2
        if reactor_id == "R2" and 20 <= day_num < 22:
            t += INTERVAL
            continue

        rows.append([t.strftime("%Y-%m-%d %H:%M"), reactor_id,
                     ph, orp, temp, cond, do_, sat, sal])
        t += INTERVAL
    return rows

if __name__ == "__main__":
    os.makedirs("demo/data", exist_ok=True)
    for r in REACTORS:
        rows = generate_rows(r, include_faults=True)
        path_clean   = f"demo/data/clean_data_{r}.csv"
        path_flagged = f"demo/data/flagged_data_{r}.csv"
        with open(path_clean, "w", newline="") as f:
            csv.writer(f).writerows([SENSORS_CLEAN] + rows)
        flagged = [[*row[:6], "Yes", *row[6:]] for row in rows]
        with open(path_flagged, "w", newline="") as f:
            csv.writer(f).writerows([SENSORS_FLAGGED] + flagged)
        print(f"{r}: {len(rows):,} rows written")
    print("Done. Add demo/data/ to .gitignore.")
