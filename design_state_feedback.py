import numpy as np
import scipy.signal as signal

# 1. Linearized Matrices (h1=8m, h2=4m)
A = np.array([[-0.25,  0.25], 
              [ 0.25, -0.50]])
B = np.array([[1.0], 
              [0.0]])
C = np.array([[0.0, 1.0]])

# 2. Check Controllability & Observability
Controllability = np.hstack((B, A @ B))
Observability = np.vstack((C, C @ A))

print("=" * 50)
print(f"Controllability Rank : {np.linalg.matrix_rank(Controllability)} (System is Controllable)")
print(f"Observability Rank   : {np.linalg.matrix_rank(Observability)} (System is Observable)")
print("=" * 50)

# 3. Design Controller Matrix K via Pole Placement
# Target closed-loop poles for fast, damped response
desired_controller_poles = np.array([-0.8, -1.2])
K = signal.place_poles(A, B, desired_controller_poles).gain_matrix

# 4. Design Observer Matrix L (Poles ~2x-5x faster than controller)
desired_observer_poles = np.array([-3.0, -4.0])
L = signal.place_poles(A.T, C.T, desired_observer_poles).gain_matrix.T

# Feedforward Gain N_bar to eliminate steady-state error
A_cl = A - B @ K
N_bar = -1.0 / (C @ np.linalg.inv(A_cl) @ B)[0, 0]

print("\nComputed Control Matrices:")
print(f"State Feedback Gain K  : {K.flatten()}")
print(f"Feedforward Gain N_bar : {N_bar:.4f}")
print(f"Observer Gain Matrix L :\n{L}")
print("=" * 50)
