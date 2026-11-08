"""Quick visualization of raw vs filtered sensor readings from the demo."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from sensor_qc.faulty_filter import filter_faulty

DATA_DIR = Path(__file__).parent / "data"

def plot_reactor(ax, df, sensor, label, color):
    ts = pd.to_datetime(df["timestamp"])
    vals = df[sensor].tolist()
    filtered = filter_faulty(ts.tolist(), vals, sensor)
    ax.plot(ts, vals, alpha=0.3, color=color, label="Raw")
    ax.plot(pd.to_datetime(filtered["ts"]), filtered["vals"],
            color=color, label=f"Filtered ({label})")
    ax.set_title(f"{label} — {sensor}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.legend(fontsize=8)

def main():
    r1 = pd.read_csv(DATA_DIR / "clean_data_R1.csv")
    r2 = pd.read_csv(DATA_DIR / "clean_data_R2.csv")

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("AzCATI Sensor QC — Raw vs Filtered", fontweight="bold")

    plot_reactor(axes[0, 0], r1, "dissolved_oxygen", "R1", "#2196F3")
    plot_reactor(axes[0, 1], r1, "oxygen_saturation", "R1", "#4CAF50")
    plot_reactor(axes[1, 0], r2, "dissolved_oxygen", "R2", "#FF5722")
    plot_reactor(axes[1, 1], r2, "oxygen_saturation", "R2", "#9C27B0")

    plt.tight_layout()
    out = DATA_DIR / "sensor_qc_plot.png"
    plt.savefig(out, dpi=150)
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
