import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# 1. Load exported simulation CSV file
df = pd.read_csv('observer_res.csv')

# Clean column headers
df.columns = df.columns.str.strip().str.replace('"', '')

# Drop duplicate time entries and ensure strictly increasing time steps
df = df.drop_duplicates(subset=['time']).sort_values(by='time').reset_index(drop=True)

time = df['time'].values
h1_true = df['h1'].values
h2_true = df['h2'].values

# System matrices and parameters
A = np.array([[-0.25,  0.25], 
              [ 0.25, -0.50]])
B = np.array([[1.0], 
              [0.0]])
C = np.array([[0.0, 1.0]])

K = np.array([1.25, 1.09])
N_bar = 3.84
L = np.array([[41.5], [6.25]])

h1_ss, h2_ss = 8.0, 4.0
href = 6.0

# Interpolate measured dy = h2 - h2_ss for observer integration
def dy_measured(t):
    return np.interp(t, time, h2_true - h2_ss)

# Observer ODE: d(x_hat)/dt = A*x_hat + B*du + L*(dy - C*x_hat)
def observer_rhs(t, x_hat):
    du = N_bar * (href - h2_ss) - np.dot(K, x_hat)
    dy = dy_measured(t)
    dy_hat = x_hat[1]
    dx_hat_dt = A @ x_hat + B.flatten() * du + L.flatten() * (dy - dy_hat)
    return dx_hat_dt

# Integrate observer state estimations
sol = solve_ivp(observer_rhs, [time[0], time[-1]], [0.0, 0.0], t_eval=time, method='RK45')
dx1_hat = sol.y[0]

# Total estimated state
h1_est = h1_ss + dx1_hat

# Calculate error
est_error = np.abs(h1_true - h1_est)

print("=" * 50)
print("       LUENBERGER OBSERVER VALIDATION        ")
print("=" * 50)
print(f"Max Estimation Error : {np.max(est_error):.4f} m")
print(f"Mean Estimation Error: {np.mean(est_error):.4f} m")
print(f"Steady-State Error   : {est_error[-1]:.6f} m")
print("=" * 50)

# Plot comparison using raw string for LaTeX label
plt.figure(figsize=(10, 5))
plt.plot(time, h1_true, 'r-', linewidth=2, label='True Tank 1 Level ($h_1$)')
plt.plot(time, h1_est, 'k--', linewidth=1.5, label=r'Observer Estimate ($\hat{h}_1$)')
plt.plot(time, h2_true, 'b-', linewidth=2, label='Measured Tank 2 Level ($h_2$)')

plt.title('State Feedback with Luenberger Observer Estimation', fontsize=12, fontweight='bold')
plt.xlabel('Time (s)', fontsize=10)
plt.ylabel('Fluid Height (m)', fontsize=10)
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()