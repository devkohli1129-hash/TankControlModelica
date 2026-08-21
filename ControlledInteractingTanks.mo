within NonInteractingTanks;

model ControlledInteractingTanks
  parameter Real A1 = 1.0, A2 = 1.0;
  parameter Real c1 = 1.0, c2 = 1.0;
  parameter Real href = 6.0; // Desired level for Tank 2 (m)
  
  // PID Controller Gains
  parameter Real Kp = 2.5;
  parameter Real Ki = 0.5;
  parameter Real Kd = 0.1;

  Real h1(start = 0.0);
  Real h2(start = 0.0);
  Real Q12;
  Real Q2;
  Real Qin; // Controlled variable
  
  Real error;
  Real error_integral(start = 0.0);
  Real error_derivative;

equation
  // Error Signal
  error = href - h2;
  der(error_integral) = error;
  error_derivative = der(error);

  // PID Control Algorithm with Flow Actuator Limits [0, 10] m³/s
  Qin = max(0.0, min(10.0, Kp * error + Ki * error_integral + Kd * error_derivative));

  // Tank Mass Balances
  Q12 = c1 * sign(h1 - h2) * sqrt(abs(h1 - h2));
  Q2 = c2 * sqrt(max(h2, 0));

  der(h1) = (Qin - Q12) / A1;
  der(h2) = (Q12 - Q2) / A2;

end ControlledInteractingTanks;
