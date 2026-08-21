import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Linearized state matrices (h1 = 8m, h2 = 4m)
A = np.array([[-0.25,  0.25], 
              [ 0.25, -0.50]])
B = np.array([[1.0], 
              [0.0]])
C = np.array([[0.0, 1.0]])
D = np.array([[0.0]])

# 1. Compute Frequency Response directly from State-Space
sys_ss = signal.StateSpace(A, B, C, D)
w = np.logspace(-2, 2, 1000)  # Frequency vector: 0.01 to 100 rad/s
w, response = signal.freqresp(sys_ss, w=w)

mag = np.abs(response)
mag_db = 20 * np.log10(mag)
phase = np.angle(response, deg=True)

# 2. Calculate Phase Margin & Gain Crossover Frequency
# Find frequency where magnitude crosses 0 dB (gain = 1.0)
crossover_idx = np.argmin(np.abs(mag - 1.0))
gain_crossover_w = w[crossover_idx]
phase_at_crossover = phase[crossover_idx]
phase_margin = 180 + phase_at_crossover

print("=" * 50)
print("        SYSTEM STABILITY MARGIN ANALYSIS        ")
print("=" * 50)
print("Gain Margin            : Infinite (Open-loop phase never crosses -180°)")
print(f"Phase Margin           : {phase_margin:.2f}°")
print(f"Gain Crossover Freq    : {gain_crossover_w:.4f} rad/s")
print("=" * 50)

# 3. Plot Open-Loop Bode Diagram
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

ax1.semilogx(w, mag_db, 'b-', linewidth=2)
ax1.axhline(0, color='gray', linestyle='--', linewidth=1, label='0 dB Crossover')
ax1.plot(gain_crossover_w, 0, 'ro', label=f'Gain Crossover ({gain_crossover_w:.2f} rad/s)')
ax1.set_title('Open-Loop Bode Plot & Stability Analysis', fontsize=12, fontweight='bold')
ax1.set_ylabel('Magnitude (dB)')
ax1.grid(True, which='both', alpha=0.3)
ax1.legend(loc='lower left')

ax2.semilogx(w, phase, 'r-', linewidth=2)
ax2.axhline(-180, color='gray', linestyle='--', linewidth=1, label='-180° Phase Limit')
ax2.plot(gain_crossover_w, phase_at_crossover, 'ro')
ax2.set_ylabel('Phase (deg)')
ax2.set_xlabel('Frequency (rad/s)')
ax2.grid(True, which='both', alpha=0.3)

plt.tight_layout()
plt.show()