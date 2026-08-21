import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# 1. State-Space Matrices (Linearized around h1=8m, h2=4m)
A = np.array([[-0.25,  0.25], 
              [ 0.25, -0.50]])
B = np.array([[1.0], 
              [0.0]])
C = np.array([[0.0, 1.0]])  # Measuring Tank 2 Height (h2)
D = np.array([[0.0]])

# 2. Derive Transfer Function G2(s) = H2(s) / Qin(s)
sys = signal.StateSpace(A, B, C, D)
tf = sys.to_tf()

print("=" * 45)
print("       LINEARIZED TRANSFER FUNCTION G2(s)     ")
print("=" * 45)
print(tf)

# 3. Calculate System Poles (Eigenvalues of Matrix A)
poles = np.linalg.eigvals(A)
print("\nSystem Poles:")
for i, p in enumerate(poles, 1):
    print(f"  Pole {i}: {p:.4f}")
print("=" * 45 + "\n")

# 4. Simulate Linearized Step Response (Step input of 1 m³/s)
t, y = signal.step(sys)

# 5. Plot the Response
plt.figure(figsize=(9, 4.5))
plt.plot(t, y, 'b-', linewidth=2, label='Linearized $\Delta h_2(t)$ Response')
plt.title('Linearized Interacting Two-Tank Step Response', fontsize=12, fontweight='bold')
plt.xlabel('Time (s)', fontsize=10)
plt.ylabel('Change in Tank 2 Height $\Delta h_2$ (m)', fontsize=10)
plt.grid(True, alpha=0.3)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()