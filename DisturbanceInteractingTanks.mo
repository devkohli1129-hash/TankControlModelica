within NonInteractingTanks;

model DisturbanceInteractingTanks
  parameter Real A1 = 1.0, A2 = 1.0;
  parameter Real c1 = 1.0, c2 = 1.0;
  parameter Real href = 6.0;
  
  // PID Gains
  parameter Real Kp = 1.2;
  parameter Real Ki = 0.2;
  parameter Real Kd = 0.4;

  Real h1(start = 0.0);
  Real h2(start = 0.0);
  Real Q12;
  Real Q2;
  Real Qin;
  Real Qleak; // Disturbance flow
  
  Real error;
  Real error_integral(start = 0.0);
  Real error_derivative;

equation
  // Sudden leak of 1.5 m³/s from Tank 2 starting at t = 25s
  Qleak = if time >= 25 then 1.5 else 0.0;

  // PID calculations
  error = href - h2;
  der(error_integral) = error;
  error_derivative = der(error);

  // Bounded control law [0, 10]
  Qin = max(0.0, min(10.0, Kp * error + Ki * error_integral + Kd * error_derivative));

  // Dynamic balance equations including leak
  Q12 = c1 * sign(h1 - h2) * sqrt(abs(h1 - h2));
  Q2 = c2 * sqrt(max(h2, 0));

  der(h1) = (Qin - Q12) / A1;
  der(h2) = (Q12 - Q2 - Qleak) / A2;

end DisturbanceInteractingTanks;
