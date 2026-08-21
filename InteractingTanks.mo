within NonInteractingTanks;

model InteractingTanks
  parameter Real A1 = 1.0, A2 = 1.0;
  parameter Real Qin = 2.0;
  parameter Real c1 = 1.0, c2 = 1.0; // Flow coefficients
  
  Real h1(start = 0.0);
  Real h2(start = 0.0);
  Real Q12; // Coupled flow rate between Tank 1 and Tank 2
  Real Q2;  // Outflow rate from Tank 2

equation
  // Flow between tanks depends on height difference (h1 - h2)
  if time <= 5 then
    Q12 = 0;
  else
    Q12 = c1 * sign(h1 - h2) * sqrt(abs(h1 - h2));
  end if;

  // Discharge flow from Tank 2
  Q2 = c2 * sqrt(max(h2, 0));

  // Mass Balance Differential Equations
  der(h1) = (Qin - Q12) / A1;
  der(h2) = (Q12 - Q2) / A2;

end InteractingTanks;
