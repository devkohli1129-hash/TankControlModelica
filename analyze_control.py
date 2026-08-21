import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load CSV data exported from OMEdit
df = pd.read_csv('ControlledTanks_res.csv')

# Standardize column names (strips quotes or whitespace)
df.columns = df.columns.str.strip().str.replace('"', '')

time = df['time'].values
h2 = df['h2'].values
href = df['href'].values if 'href' in df.columns else np.full_like(time, 6.0)

# 2. Compute Performance Metrics
target = href[-1]
peak_val = np.max(h2)
peak_time = time[np.argmax(h2)]
percent_overshoot = ((peak_val - target) / target) * 100

# 10% to 90% Rise Time
idx_10 = np.argmax(h2 >= 0.1 * target)
idx_90 = np.argmax(h2 >= 0.9 * target)
rise_time = time[idx_90] - time[idx_10]

# 2% Settling Time
band = 0.02 * target
settled_indices = np.where(np.abs(h2 - target) <= band)[0]
# Find where it enters and stays within band
settling_time = time[-1]
for i in range(len(settled_indices) - 1):
    if np.all(np.abs(h2[settled_indices[i]:] - target) <= band):
        settling_time = time[settled_indices[i]]
        break

print("=" * 45)
print("      PID CONTROL PERFORMANCE METRICS        ")
print("=" * 45)
print(f"Target Level (href)  : {target:.2f} m")
print(f"Peak Height (h2_max) : {peak_val:.2f} m at t = {peak_time:.2f} s")
print(f"Percent Overshoot    : {percent_overshoot:.2f}%")
print(f"Rise Time (10-90%)   : {rise_time:.2f} s")
print(f"2% Settling Time     : {settling_time:.2f} s")
print("=" * 45)

# 3. Plot Controller Response
plt.figure(figsize=(9, 4.5))
plt.plot(time, h2, 'r-', linewidth=2, label='Tank 2 Height ($h_2$)')
plt.plot(time, href, 'b--', linewidth=1.5, label='Setpoint ($h_{ref} = 6.0\\text{m}$)')
plt.axhline(target * 1.02, color='gray', linestyle=':', alpha=0.6, label='±2% Settling Band')
plt.axhline(target * 0.98, color='gray', linestyle=':', alpha=0.6)

plt.title('PID Closed-Loop Tank Level Control', fontsize=12, fontweight='bold')
plt.xlabel('Time (s)', fontsize=10)
plt.ylabel('Fluid Height (m)', fontsize=10)
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()