import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_simulation_data():
    # 1. Search in current working directory first
    csv_files = glob.glob("*.csv")
    
    # 2. Search in OpenModelica default temp directory if not found locally
    if not csv_files:
        temp_dir = r"C:\Users\Dev\AppData\Local\Temp\OpenModelica\OMEdit\NonInteractingTanks.TwoConnectedTanks"
        csv_files = glob.glob(os.path.join(temp_dir, "*.csv"))
        
    if not csv_files:
        raise FileNotFoundError(
            "Could not find any .csv files in the current folder or OMEdit temp folder.\n"
            "Please export the CSV from OMEdit (File -> Export -> Export Variables / CSV) "
            "into your project folder."
        )
    
    csv_path = csv_files[0]
    print(f"[+] Loading simulation data from: {csv_path}\n")
    
    df = pd.read_csv(csv_path)
    
    # Clean column headers (OpenModelica often wraps header names in double quotes)
    df.columns = df.columns.str.replace('"', '').str.strip()
    return df

def analyze_and_plot():
    df = load_simulation_data()
    
    # Find relevant column names flexibly
    time_col = [c for c in df.columns if 'time' in c.lower()][0]
    h1_col = [c for c in df.columns if 'tank1.h' in c.lower()][0]
    
    # Check if tank2.h is present, fallback to tank2.Q1 if h was not recorded
    h2_cols = [c for c in df.columns if 'tank2.h' in c.lower()]
    h2_col = h2_cols[0] if h2_cols else None

    t = df[time_col].values
    h1 = df[h1_col].values

    # --- Metric Calculations ---
    h1_ss = h1[-1]  # Steady-state height (~4.0 m)
    peak_h1 = np.max(h1)
    t_peak = t[np.argmax(h1)]

    # 95% Settling Time Calculation (time after which h1 stays within 5% of h1_ss)
    tolerance = 0.05 * h1_ss
    out_of_bounds_indices = np.where(np.abs(h1 - h1_ss) > tolerance)[0]
    t_settling = t[out_of_bounds_indices[-1]] if len(out_of_bounds_indices) > 0 else t[0]

    # --- Print Summary Metrics ---
    print("=" * 40)
    print("     TANK 1 DYNAMIC METRICS SUMMARY     ")
    print("=" * 40)
    print(f"Peak Height (h1_max)   : {peak_h1:.3f} m (at t = {t_peak:.1f} s)")
    print(f"Steady-State Height    : {h1_ss:.3f} m")
    print(f"95% Settling Time (ts) : {t_settling:.3f} s")
    print("=" * 40 + "\n")

    # --- Plotting ---
    plt.figure(figsize=(10, 5))
    plt.plot(t, h1, 'r-', label='Tank 1 Height ($h_1$)', linewidth=2)
    
    if h2_col:
        h2 = df[h2_col].values
        plt.plot(t, h2, 'b--', label='Tank 2 Height ($h_2$)', linewidth=2)
        
    plt.axhline(y=h1_ss, color='k', linestyle=':', label=f'Steady State ({h1_ss:.1f} m)')
    plt.axvline(x=t_settling, color='g', linestyle='--', label=f'95% Settling Time ({t_settling:.1f} s)')

    plt.title('Non-Interacting Two-Tank Dynamic Response Analysis', fontsize=12, fontweight='bold')
    plt.xlabel('Time (s)', fontsize=10)
    plt.ylabel('Liquid Height (m)', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_and_plot()