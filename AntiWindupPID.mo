within NonInteractingTanks;

model AntiWindupPID
  // Physical Parameters
  parameter Real A1 = 1.0, A2 = 1.0;
  parameter Real c1 = 1.0, c2 = 1.0;
  parameter Real href = 6.0;

  // Optimized ITAE Control Gains
  parameter Real Kp = 1.7505, Ki = 0.4598, Kd = 0.0076;
  parameter Real T_aw = 0.5; // Anti-windup tracking time constant

  Real h1(start = 0.0), h2(start = 0.0);
  Real Q12, Q2, Qin, Qin_unsat;
  Real error, error_derivative;
  Real error_integral(start = 0.0);

equation
  error = href - h2;
  error_derivative = der(error);

  // Unsaturated Controller Command Signal
  Qin_unsat = Kp * error + Ki * error_integral + Kd * error_derivative;

  // Smooth Actuator Saturation [0, 10] m3/s
  Qin = smooth(1, if Qin_unsat > 10.0 then 10.0 else if Qin_unsat < 0.0 then 0.0 else Qin_unsat);

  // Anti-Windup Back-Calculation Integrator
  der(error_integral) = error + (1.0 / T_aw) * (Qin - Qin_unsat);

  // Smooth Non-Linear Flow Dynamics (prevents initialization crash)
  Q12 = c1 * smooth(1, if h1 >= h2 then sqrt(max(1e-6, h1 - h2)) else -sqrt(max(1e-6, h2 - h1)));
  Q2 = c2 * sqrt(noEvent(max(0.0, h2)));

  der(h1) = (Qin - Q12) / A1;
  der(h2) = (Q12 - Q2) / A2;

end AntiWindupPID;
