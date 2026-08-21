import numpy as np
from scipy.optimize import minimize
from scipy.integrate import solve_ivp

# Define non-linear 2-tank plant dynamics
def plant_dynamics(t, x, Qin):
    h1, h2 = x
    h1 = max(0.0, h1)
    h2 = max(0.0, h2)
    
    A1, A2 = 1.0, 1.0
    c1, c2 = 1.0, 1.0
    
    Q12 = c1 * np.sign(h1 - h2) * np.sqrt(abs(h1 - h2))
    Q2 = c2 * np.sqrt(h2)
    
    dh1dt = (Qin - Q12) / A1
    dh2dt = (Q12 - Q2) / A2
    return [dh1dt, dh2dt]

# ITAE Cost Function: Integral of t * |error| dt
def calculate_itae(gains):
    Kp, Ki, Kd = gains
    href = 6.0
    
    # Simulation loop with bounded PID logic
    def closed_loop(t, state):
        h1, h2, err_int, prev_err = state
        err = href - h2
        
        # Approximate derivative
        derr = (err - prev_err) / 0.01 if t > 0 else 0.0
        
        # Bounded PID control
        Qin = max(0.0, min(10.0, Kp * err + Ki * err_int + Kd * derr))
        
        dh1dt, dh2dt = plant_dynamics(t, [h1, h2], Qin)
        return [dh1dt, dh2dt, err, 0.0]

    # Quick integration over 30s
    t_eval = np.linspace(0, 30, 300)
    sol = solve_ivp(closed_loop, [0, 30], [0.0, 0.0, 0.0, 6.0], t_eval=t_eval)
    
    h2 = sol.y[1]
    error = href - h2
    itae = np.trapz(t_eval * np.abs(error), t_eval)
    return itae

# Initial guess [Kp, Ki, Kd]
initial_gains = [1.2, 0.2, 0.4]
res = minimize(calculate_itae, initial_gains, method='Nelder-Mead')

opt_Kp, opt_Ki, opt_Kd = res.x

print("=" * 50)
print("       ITAE AUTOMATED GAIN OPTIMIZATION        ")
print("=" * 50)
print(f"Optimal Kp : {opt_Kp:.4f}")
print(f"Optimal Ki : {opt_Ki:.4f}")
print(f"Optimal Kd : {opt_Kd:.4f}")
print(f"Minimized ITAE Index Value : {res.fun:.4f}")
print("=" * 50)