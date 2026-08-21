# OpenModelica Executable Runner (PyQt6 Desktop App)

**FOSSEE / OpenModelica Screening Task 2 Submission**  
**Repository:** [https://github.com/devkohli1129-hash/TankControlModelica](https://github.com/devkohli1129-hash/TankControlModelica)

---

## 📌 Project Overview

This repository contains the complete implementation for **Screening Task 2: Desktop App for OpenModelica using Python and PyQt**.

The project accomplishes two key milestones:
1. **Compilation of Physical Models:** The `TwoConnectedTanks` model from the `NonInteractingTanks` package was compiled in OpenModelica into a standalone native executable (`TwoConnectedTanks.exe`), packaged alongside all required runtime libraries and dependencies.
2. **Interactive Desktop GUI Application:** A modular, Object-Oriented desktop application built in **Python 3 and PyQt6** to parameterize, execute, and analyze OpenModelica simulation binaries with live graphical results, variable filtering, and data export.

---

## 🎯 Task Requirements & Compliance Matrix

| Requirement | Implementation Status | Details |
| :--- | :---: | :--- |
| **Compile `TwoConnectedTanks` model** | ✅ Completed | Standalone binary generated in `bin/` alongside `.xml`, `.json`, and runtime `.dll` files. |
| **Collect runtime dependencies** | ✅ Completed | Bundled all 20+ required dynamic runtime libraries (`libSimulationRuntimeC`, `openblas`, `sundials`, etc.) in `bin/`. |
| **Field 1: Select Application** | ✅ Completed | `QLineEdit` + `QFileDialog` file browser for selecting the `.exe` binary. |
| **Field 2: Start Time (Integer)** | ✅ Completed | `QSpinBox` enforcing integer start time. |
| **Field 3: Stop Time (Integer)** | ✅ Completed | `QSpinBox` enforcing integer stop time. |
| **Condition: $0 \le t_{\text{start}} < t_{\text{stop}} < 5$** | ✅ Completed | Validated at both UI widget level and programmatic assertion before execution. |
| **Execution with `-override` flags** | ✅ Completed | Passes `-override startTime=...,stopTime=...` flags per OpenModelica specification. |
| **Interactive Plotting & Post-Processing** | 🌟 Extra Feature | Live PyQt6 plot canvas parsing Modelica `.mat` files with dynamic variable toggle and PNG/CSV exports. |
| **Object-Oriented Design & PEP8** | ✅ Completed | Structured into dedicated classes (`OpenModelicaRunnerApp`, `PlotWindow`) with clean type annotations. |

---

## 🏗️ Software Architecture & Design

The desktop application follows modular Object-Oriented Programming (OOP) principles:

```
TankControlModelica/
│
├── bin/                                # Compiled OpenModelica simulation bundle
│   ├── TwoConnectedTanks.exe           # Standalone compiled model executable
│   ├── TwoConnectedTanks_init.xml      # Model initialization parameters
│   ├── TwoConnectedTanks_info.json     # Model variable & equation metadata
│   ├── TwoConnectedTanks_JacA.bin      # Jacobian sparsity matrix
│   └── *.dll                           # 64-bit runtime libraries (sundials, openblas, etc.)
│
├── NonInteractingTanks/                # Modelica physical source files
│   ├── TwoConnectedTanks.mo            # Main composite two-tank model
│   ├── Tank.mo                         # Tank 1 dynamic equations (Qin, Qo, h)
│   ├── Tank2.mo                        # Tank 2 dynamic equations (Q1, h, T)
│   ├── FlowConnect.mo                  # Fluid connector definition
│   └── package.mo                      # Modelica package declaration
│
├── gui.py                              # Main PyQt6 Desktop Application
├── requirements.txt                    # Python package dependencies
├── README.md                           # Documentation & user guide
└── .gitignore                          # Repository hygiene
```

### Class Architecture

1. **`OpenModelicaRunnerApp (QWidget)`**:
   - Manages main window UI, input fields, validation logic, and subprocess execution.
   - Executes OpenModelica binaries in their native directory context (`cwd=exe_dir`) with customized simulation flags.
   - Reads and parses the resulting binary MAT-file (`<model>_res.mat`).

2. **`PlotWindow (QWidget)`**:
   - A dedicated visualization window.
   - Decoupled from GUI backend crashes by using pure Matplotlib `Agg` buffer rendering converted into native `QPixmap`.
   - Features real-time checkbox selection for states (`tank1.h`, `tank2.h`, etc.), CSV export, and high-resolution PNG generation.

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
- **OS:** Windows 10/11 or Linux
- **Python:** Python 3.8 to 3.13

### 2. Setup Environment
Clone the repository and install the required Python packages:

```bash
git clone https://github.com/devkohli1129-hash/TankControlModelica.git
cd TankControlModelica

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate     # On Windows
# source venv/bin/activate # On Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
Launch the GUI application:

```bash
python gui.py
```

---

## 💻 Step-by-Step Usage Guide

1. **Select Executable:** Click **Browse** and choose `bin/TwoConnectedTanks.exe` (or any other compiled OpenModelica binary).
2. **Configure Time Parameters:**
   - **Start Time ($s$):** Choose an integer between $0$ and $4$.
   - **Stop Time ($s$):** Choose an integer between $1$ and $4$ (must be strictly greater than Start Time).
3. **Run Simulation:** Click **Run Simulation & Plot**.
4. **Inspect & Export Results:**
   - The interactive plot window will open automatically displaying liquid levels ($h_1$ and $h_2$).
   - Toggle checkboxes on the left to show or hide variables.
   - Click **Save Plot as PNG...** or **Export Data to CSV...** to save the results.

---

## 🧪 Physical Model Analysis (`TwoConnectedTanks`)

The physical system models two liquid tanks in series:

* **Tank 1 Dynamics:**
  $$\frac{dh_1}{dt} = \frac{Q_{\text{in}} - Q_o}{A_1}, \quad \text{where } Q_{\text{in}} = 2\,\text{m}^3/\text{s}$$
  For $t \le 5\,\text{s}$, the outlet valve is closed ($Q_o = 0$), producing a steady ramp:
  $$h_1(t) = h_1(0) + \frac{2}{1}t = 2t\,\text{m}$$
* **Tank 2 Dynamics:**
  $$\frac{dh_2}{dt} = \frac{Q_1}{A_2} = \frac{Q_o}{A_2}$$
  Since $Q_o = 0$ for $t \le 5\,\text{s}$, $h_2(t) = 0.0\,\text{m}$.

---

## 📄 License & Attribution

Developed by **Dev Kohli** for the **FOSSEE OpenModelica Screening Selection**.
Modelica package based on FOSSEE screening assets.
