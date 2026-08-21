import sys
import os
import warnings

# Suppress harmless SIP / PyQt deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import subprocess
import traceback
import numpy as np

# Force pure Agg software backend to prevent Qt C-binding crashes on Python 3.13
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from scipy.io import loadmat

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox,
    QListWidget, QListWidgetItem, QGroupBox, QScrollArea, QSplitter
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt


class PlotWindow(QWidget):
    """Interactive simulation results window featuring variable toggling,
    clean Matplotlib rendering via Agg (100% crash-proof on Python 3.13),
    exporting to PNG and CSV, and full-resolution image preview."""

    def __init__(self, title: str, model_name: str, exe_dir: str, time_vector: np.ndarray, series_dict: dict) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(900, 550)
        self.resize(1000, 620)

        self.model_name = model_name
        self.exe_dir = exe_dir
        self.time_vector = time_vector
        self.series_dict = series_dict  # name: (x, y, style)
        self.current_png_path = os.path.join(exe_dir, f"{model_name}_plot.png")
        self._raw_pixmap = None

        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Header
        header = QLabel(f"Simulation Analysis: <b>{self.model_name}</b>")
        header.setFont(QFont("Segoe UI", 11))
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel: Variable Selection & Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        var_group = QGroupBox("Select Variables to Plot")
        var_layout = QVBoxLayout(var_group)

        self.var_list = QListWidget()
        
        # Check if there are any '.h' or 'h' (level/height) variables
        has_height_vars = any(
            name.lower().endswith('.h') or name.lower() in ('h', 'h1', 'h2')
            for name in self.series_dict
        )

        for name in self.series_dict:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Smart default selection:
            # Prefer liquid level states (e.g. tank1.h, tank2.h)
            # Exclude extreme residence times like tank2.T or derivatives by default
            is_level_var = name.lower().endswith('.h') or name.lower() in ('h', 'h1', 'h2')
            is_derivative = 'der(' in name.lower()
            is_residence_time = name.lower().endswith('.t') or name.lower() == 't'
            
            if has_height_vars:
                should_check = is_level_var
            else:
                should_check = self.series_dict[name][2] == '-' and not is_derivative and not is_residence_time
                
            item.setCheckState(Qt.CheckState.Checked if should_check else Qt.CheckState.Unchecked)
            self.var_list.addItem(item)
            
        self.var_list.itemChanged.connect(self.update_plot)
        var_layout.addWidget(self.var_list)

        # Selection button helpers
        btn_box = QHBoxLayout()
        sel_all_btn = QPushButton("Select All")
        sel_all_btn.clicked.connect(self.select_all_vars)
        desel_all_btn = QPushButton("Deselect All")
        desel_all_btn.clicked.connect(self.deselect_all_vars)
        btn_box.addWidget(sel_all_btn)
        btn_box.addWidget(desel_all_btn)
        var_layout.addLayout(btn_box)

        left_layout.addWidget(var_group, 2)

        # Action Buttons
        act_group = QGroupBox("Export & Actions")
        act_layout = QVBoxLayout(act_group)

        save_png_btn = QPushButton("💾 Save Plot as PNG...")
        save_png_btn.clicked.connect(self.save_png_dialog)
        act_layout.addWidget(save_png_btn)

        open_img_btn = QPushButton("🖼️ Open in Image Viewer")
        open_img_btn.clicked.connect(self.open_image_externally)
        act_layout.addWidget(open_img_btn)

        export_csv_btn = QPushButton("📊 Export Data to CSV...")
        export_csv_btn.clicked.connect(self.export_csv_dialog)
        act_layout.addWidget(export_csv_btn)

        left_layout.addWidget(act_group, 1)
        splitter.addWidget(left_widget)

        # Right Panel: Plot Canvas
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.plot_label = QLabel()
        self.plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plot_label.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px;")
        right_layout.addWidget(self.plot_label)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Initial Plot Render
        self.update_plot()

    def select_all_vars(self) -> None:
        self.var_list.blockSignals(True)
        for i in range(self.var_list.count()):
            self.var_list.item(i).setCheckState(Qt.CheckState.Checked)
        self.var_list.blockSignals(False)
        self.update_plot()

    def deselect_all_vars(self) -> None:
        self.var_list.blockSignals(True)
        for i in range(self.var_list.count()):
            self.var_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.var_list.blockSignals(False)
        self.update_plot()

    def update_plot(self) -> None:
        # Create figure and canvas with clean styling
        fig = Figure(figsize=(8.5, 5.5), dpi=120, facecolor='#ffffff')
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        has_data = False
        for i in range(self.var_list.count()):
            item = self.var_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                name = item.text()
                if name in self.series_dict:
                    x, y, style = self.series_dict[name]
                    ax.plot(x, y, style, label=name, linewidth=2)
                    has_data = True

        ax.set_title(f"Simulation Results: {self.model_name}", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Time (s)", fontsize=11, labelpad=8)
        ax.set_ylabel("Liquid Level / Variable Value", fontsize=11, labelpad=8)
        ax.grid(True, linestyle='--', alpha=0.5)

        if has_data:
            ax.legend(loc='best', framealpha=0.9)
        else:
            ax.text(
                0.5, 0.5, "No variables selected.\nPlease check variables on the left.",
                transform=ax.transAxes, ha='center', va='center', fontsize=12, color='gray'
            )

        fig.tight_layout()
        canvas.draw()

        # Save default png automatically to exe folder
        try:
            fig.savefig(self.current_png_path, dpi=150)
        except Exception:
            pass

        # Convert buffer to QPixmap
        rgba = np.asarray(canvas.buffer_rgba())
        h, w, c = rgba.shape
        qimg = QImage(rgba.data, w, h, w * c, QImage.Format.Format_RGBA8888)
        self._raw_pixmap = QPixmap.fromImage(qimg)
        self._render_scaled_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render_scaled_pixmap()

    def _render_scaled_pixmap(self) -> None:
        if self._raw_pixmap and not self._raw_pixmap.isNull():
            target_size = self.plot_label.size()
            if target_size.width() > 50 and target_size.height() > 50:
                scaled = self._raw_pixmap.scaled(
                    target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.plot_label.setPixmap(scaled)
            else:
                self.plot_label.setPixmap(self._raw_pixmap)

    def save_png_dialog(self) -> None:
        default_path = os.path.join(self.exe_dir, f"{self.model_name}_plot.png")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot Image", default_path, "PNG Image (*.png);;All Files (*)"
        )
        if file_path:
            try:
                import shutil
                if os.path.exists(self.current_png_path) and os.path.abspath(file_path) != os.path.abspath(self.current_png_path):
                    shutil.copyfile(self.current_png_path, file_path)
                QMessageBox.information(self, "Saved", f"Plot saved successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image:\n{e}")

    def open_image_externally(self) -> None:
        if os.path.exists(self.current_png_path):
            if sys.platform.startswith("win"):
                os.startfile(self.current_png_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.current_png_path])
            else:
                subprocess.run(["xdg-open", self.current_png_path])
        else:
            QMessageBox.warning(self, "Warning", "Plot image has not been generated yet.")

    def export_csv_dialog(self) -> None:
        default_path = os.path.join(self.exe_dir, f"{self.model_name}_exported.csv")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Simulation Data to CSV", default_path, "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            try:
                # Find max length of dynamic time series
                rows = []
                headers = ["time"]
                col_data = [self.time_vector]

                for name, (x, y, style) in self.series_dict.items():
                    if len(y) == len(self.time_vector):
                        headers.append(name)
                        col_data.append(y)

                stacked = np.column_stack(col_data)
                np.savetxt(file_path, stacked, delimiter=",", header=",".join(headers), comments="", fmt="%g")
                QMessageBox.information(self, "Exported", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{e}")


class OpenModelicaRunnerApp(QWidget):
    """PyQt6 Desktop Application to execute OpenModelica compiled binaries and plot results."""

    def __init__(self) -> None:
        super().__init__()
        self.plot_window = None
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("OpenModelica Executable Runner - Screening Task 2")
        self.setMinimumWidth(520)

        layout = QVBoxLayout()

        # Input Field 1: Executable Selector
        exec_layout = QHBoxLayout()
        self.exec_label = QLabel("Executable:")
        self.exec_input = QLineEdit()
        self.exec_input.setPlaceholderText("Select compiled OpenModelica executable...")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        exec_layout.addWidget(self.exec_label)
        exec_layout.addWidget(self.exec_input)
        exec_layout.addWidget(self.browse_btn)
        layout.addLayout(exec_layout)

        # Input Field 2: Start Time Integer Input
        start_layout = QHBoxLayout()
        self.start_label = QLabel("Start Time (s):")
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 4)
        self.start_spin.setValue(0)
        start_layout.addWidget(self.start_label)
        start_layout.addWidget(self.start_spin)
        layout.addLayout(start_layout)

        # Input Field 3: Stop Time Integer Input
        stop_layout = QHBoxLayout()
        self.stop_label = QLabel("Stop Time (s):")
        self.stop_spin = QSpinBox()
        self.stop_spin.setRange(1, 4)
        self.stop_spin.setValue(1)
        stop_layout.addWidget(self.stop_label)
        stop_layout.addWidget(self.stop_spin)
        layout.addLayout(stop_layout)

        # Run Button
        self.run_btn = QPushButton("Run Simulation & Plot")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.run_btn.clicked.connect(self.run_executable)
        layout.addWidget(self.run_btn)

        self.setLayout(layout)

    def browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select OpenModelica Executable", "", "Executables (*.exe *);;All Files (*)"
        )
        if file_path:
            self.exec_input.setText(file_path)

    def run_executable(self) -> None:
        exe_path = self.exec_input.text().strip()
        start_time = self.start_spin.value()
        stop_time = self.stop_spin.value()

        if not exe_path or not os.path.exists(exe_path):
            QMessageBox.critical(self, "Error", "Please select a valid executable file.")
            return

        if not (0 <= start_time < stop_time < 5):
            QMessageBox.warning(
                self, 
                "Invalid Parameters", 
                "Condition failed: Ensure 0 <= start_time < stop_time < 5."
            )
            return

        exe_dir = os.path.dirname(os.path.abspath(exe_path))
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]

        cmd = [
            exe_path,
            "-override",
            f"startTime={start_time},stopTime={stop_time}"
        ]

        try:
            result = subprocess.run(
                cmd, 
                cwd=exe_dir, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            QMessageBox.information(
                self, 
                "Success", 
                "Simulation finished successfully!\nOpening plot..."
            )

            self.plot_results(exe_dir, exe_name)

        except subprocess.CalledProcessError as err:
            error_output = err.stderr.strip() or err.stdout.strip() or str(err)
            QMessageBox.critical(self, "Execution Error", f"OpenModelica Error:\n{error_output}")
        except Exception as err:
            QMessageBox.critical(self, "Execution Error", f"Failed to run executable:\n{err}")

    def plot_results(self, exe_dir: str, model_name: str) -> None:
        mat_path = os.path.join(exe_dir, f"{model_name}_res.mat")
        if not os.path.exists(mat_path):
            QMessageBox.warning(self, "Warning", f"Result file not found:\n{mat_path}")
            return

        try:
            mat_data = loadmat(mat_path)
            names_raw = mat_data.get('name')
            data_info = mat_data.get('dataInfo')
            data_1 = mat_data.get('data_1')
            data_2 = mat_data.get('data_2')

            if names_raw is None or data_info is None or data_2 is None:
                QMessageBox.warning(self, "Warning", "Result file did not contain expected variables.")
                return

            # In Modelica MAT format, dataInfo is a 4 x N matrix
            if data_info.shape[0] != 4 and data_info.ndim == 2 and data_info.shape[1] == 4:
                data_info = data_info.T

            num_vars = data_info.shape[1] if data_info.ndim == 2 else len(names_raw)

            # Reconstruct variable names from the character matrix
            var_names = []
            if names_raw.ndim == 1:
                for j in range(num_vars):
                    chars = [names_raw[i][j] for i in range(len(names_raw)) if j < len(names_raw[i])]
                    name_str = "".join(chars).strip().replace('\x00', '')
                    var_names.append(name_str)
            elif names_raw.ndim == 2:
                if names_raw.shape[1] == num_vars:
                    for j in range(num_vars):
                        chars = [chr(int(c)) if isinstance(c, (int, np.integer)) else str(c) for c in names_raw[:, j]]
                        name_str = "".join(chars).strip().replace('\x00', '')
                        var_names.append(name_str)
                else:
                    for j in range(num_vars):
                        chars = [chr(int(c)) if isinstance(c, (int, np.integer)) else str(c) for c in names_raw[j, :]]
                        name_str = "".join(chars).strip().replace('\x00', '')
                        var_names.append(name_str)

            time_vector = data_2[0]
            series_dict = {}

            # Extract variables (skipping 'time')
            for i, name in enumerate(var_names):
                if not name or 'time' in name.lower():
                    continue

                block = int(data_info[0, i])
                raw_idx = int(data_info[1, i])
                row_idx = abs(raw_idx) - 1
                sign = -1 if raw_idx < 0 else 1

                label = name if name else f"State {i}"
                if block == 2 and 0 <= row_idx < data_2.shape[0]:
                    values = sign * data_2[row_idx]
                    series_dict[label] = (time_vector, values, '-')
                elif block == 1 and data_1 is not None and 0 <= row_idx < data_1.shape[0]:
                    val = sign * data_1[row_idx][-1]
                    series_dict[label] = ([time_vector[0], time_vector[-1]], [val, val], '--')

            # Fallback if dictionary is empty
            if not series_dict:
                for idx in range(1, min(5, data_2.shape[0])):
                    series_dict[f"State {idx}"] = (time_vector, data_2[idx], '-')

            # Display crash-proof interactive plot window
            self.plot_window = PlotWindow(
                title=f"Simulation Results - {model_name}",
                model_name=model_name,
                exe_dir=exe_dir,
                time_vector=time_vector,
                series_dict=series_dict
            )
            self.plot_window.show()
            self.plot_window.raise_()
            self.plot_window.activateWindow()

        except Exception:
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Plot Error", f"Failed to plot results:\n{error_details[-500:]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenModelicaRunnerApp()
    window.show()
    sys.exit(app.exec())