import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load exported simulation CSV files
df_pid = pd.read_csv('dist_res.csv')
df_ff = pd.read_csv('ff_res.csv')

# 2. Clean up column header formatting
df_pid.columns = df_pid.columns.str.strip().str.replace('"', '')
df_ff.columns = df_ff.columns.str.strip().str.replace('"', '')

# Extract variables
t_pid = df_pid['time'].values
h2_pid = df_pid['h2'].values

t_ff = df_ff['time'].values
h2_ff = df_ff['h2'].values

href = df_pid['href'].values if 'href' in df_pid.columns else np.full_like(t_pid, 6.0)

# 3. Calculate Performance Metrics During Disturbance (t >= 25s)
dist_start_idx_pid = np.argmax(t_pid >= 25.0)
dist_start_idx_ff = np.argmax(t_ff >= 25.0)

min_h2_pid = np.min(h2_pid[dist_start_idx_pid:])
min_h2_ff = np.min(h2_ff[dist_start_idx_ff:])

drop_pid = 6.0 - min_h2_pid
drop_ff = 6.0 - min_h2_ff

print("=" * 50)
print("      DISTURBANCE REJECTION ANALYSIS (t >= 25s)   ")
print("=" * 50)
print(f"PID Feedback Minimum Height : {min_h2_pid:.2f} m (Level Drop: {drop_pid:.2f} m)")
print(f"PID + Feedforward Min Height: {min_h2_ff:.2f} m (Level Drop: {drop_ff:.2f} m)")
print(f"Disturbance Mitigation Gain : {((drop_pid - drop_ff) / drop_pid) * 100:.1f}% reduction in level drop")
print("=" * 50 + "\n")

# 4. Generate Plot
plt.figure(figsize=(10, 5))
plt.plot(t_pid, h2_pid, 'r-', linewidth=2, label='PID Feedback Only')
plt.plot(t_ff, h2_ff, 'g--', linewidth=2, label='PID + Feedforward Action')
plt.axvline(25, color='black', linestyle=':', linewidth=1.5, label='Leak Disturbance Injected (t = 25s)')
plt.axhline(6.0, color='blue', linestyle='-.', alpha=0.7, label='Setpoint ($h_{ref} = 6.0\\text{m}$)')

plt.title('Disturbance Rejection Comparison (1.5 m³/s Pipe Leak at t = 25s)', fontsize=12, fontweight='bold')
plt.xlabel('Time (s)', fontsize=10)
plt.ylabel('Tank 2 Level $h_2$ (m)', fontsize=10)
plt.grid(True, alpha=0.3)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()