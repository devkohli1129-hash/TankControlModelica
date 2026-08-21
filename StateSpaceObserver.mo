within NonInteractingTanks;

model StateSpaceObserver
  // Physical parameters
  parameter Real A1 = 1.0, A2 = 1.0;
  parameter Real c1 = 1.0, c2 = 1.0;
  parameter Real href = 6.0;

  // Computed Gains from Python Pole Placement
  parameter Real K[1,2] = [1.25, 1.09];
  parameter Real N_bar = 3.84;
  parameter Real L[2,1] = [41.5; 6.25];

  // Operating Point (Linearization Center)
  parameter Real h1_ss = 8.0;
  parameter Real h2_ss = 4.0;
  parameter Real Qin_ss = 2.0;

  // True Physical States
  Real h1(start = 8.0);
  Real h2(start = 4.0);
  Real Q12, Q2, Qin;

  // Linearized Deviations (Delta x)
  Real dx1, dx2, dy;

  // Observer Estimated Deviation States (x_hat)
  Real dx1_hat(start = 0.0);
  Real dx2_hat(start = 0.0);
  Real dy_hat;

  // Calculated Control Deviation (du)
  Real du;

equation
  // Actual Non-Linear Plant Dynamics
  Q12 = c1 * sign(h1 - h2) * sqrt(abs(h1 - h2));
  Q2 = c2 * sqrt(max(h2, 0));
  der(h1) = (Qin - Q12) / A1;
  der(h2) = (Q12 - Q2) / A2;

  // Measure Deviation from Operating Point
  dx1 = h1 - h1_ss;
  dx2 = h2 - h2_ss;
  dy = dx2; // Measured output (Tank 2 height deviation)

  // Observer Output Deviation
  dy_hat = dx2_hat;

  // State Feedback Control Law: du = N_bar * r - K * x_hat
  du = N_bar * (href - h2_ss) - (K[1,1] * dx1_hat + K[1,2] * dx2_hat);
  Qin = max(0.0, min(10.0, Qin_ss + du));

  // Luenberger State Observer Equations: d(x_hat)/dt = A*x_hat + B*du + L*(y - y_hat)
  der(dx1_hat) = (-0.25 * dx1_hat + 0.25 * dx2_hat) + 1.0 * du + L[1,1] * (dy - dy_hat);
  der(dx2_hat) = ( 0.25 * dx1_hat - 0.50 * dx2_hat) + 0.0 * du + L[2,1] * (dy - dy_hat);

end StateSpaceObserver;
