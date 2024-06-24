import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QSlider, \
    QComboBox, QListWidget, QCheckBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class WavePacketApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animacja Paczek Falowych")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.canvas = FigureCanvas(plt.figure())
        self.layout.addWidget(self.canvas)

        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_xlabel('Odległość')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Animacja Paczek Falowych')

        self.add_packet_button = QPushButton('Dodaj Paczkę Falową')
        self.add_packet_button.clicked.connect(self.add_wave_packet)
        self.layout.addWidget(self.add_packet_button)

        self.remove_packet_button = QPushButton('Usuń Paczkę Falową')
        self.remove_packet_button.clicked.connect(self.remove_wave_packet)
        self.layout.addWidget(self.remove_packet_button)

        self.start_animation_button = QPushButton('Start Animacji')
        self.start_animation_button.clicked.connect(self.start_animation)
        self.layout.addWidget(self.start_animation_button)

        self.stop_animation_button = QPushButton('Zatrzymaj Animację')
        self.stop_animation_button.clicked.connect(self.stop_animation)
        self.layout.addWidget(self.stop_animation_button)

        self.reset_values_button = QPushButton('Przywróć wartości domyślne')
        self.reset_values_button.clicked.connect(self.reset_values)
        self.layout.addWidget(self.reset_values_button)

        self.k_slider, self.k_label = self.create_slider('Liczba falowa (k)', -10.0, 10.0, 0.01, 2)
        self.vg_slider, self.vg_label = self.create_slider('Prędkość grupowa', -10.0, 10.0, 0.01, 2)
        self.amplitude_slider, self.amplitude_label = self.create_slider('Amplituda', -10.0, 10.0, 0.01, 2)
        self.phase_velocity_slider, self.phase_velocity_label = self.create_slider('Prędkość fazowa', -5.0, 5.0, 0.1, 2)

        self.wave_type_combo = QComboBox()
        self.wave_type_combo.addItem("sinusoidalna")
        self.wave_type_combo.addItem("cosinusoidalna")
        self.layout.addWidget(QLabel('Typ fali:'))
        self.layout.addWidget(self.wave_type_combo)

        self.invert_wave_checkbox = QCheckBox("Odwróć falę")
        self.layout.addWidget(self.invert_wave_checkbox)

        self.packet_list = QListWidget()
        self.layout.addWidget(QLabel('Lista paczek falowych:'))
        self.layout.addWidget(self.packet_list)

        self.packets = []
        self.time = np.linspace(0, 20, 2000)
        self.animation = None

    def create_slider(self, label, min_val, max_val, step, default_value):
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(150)  # Set a fixed minimum width for labels
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(int((max_val - min_val) / step))
        slider.setValue(int((default_value - min_val) / step))
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        value_label = QLabel(f'{default_value:.2f}')
        slider.valueChanged.connect(lambda: self.slider_value_changed(slider, value_label, min_val, step))

        slider_layout = QHBoxLayout()  # New layout to center slider and value label
        spacer_left = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        slider_layout.addSpacerItem(spacer_left)
        slider_layout.addWidget(slider)
        slider_layout.addWidget(value_label)
        slider_layout.addSpacerItem(spacer_right)

        layout.addWidget(label_widget)
        layout.addLayout(slider_layout)
        self.layout.addLayout(layout)
        return slider, value_label

    def slider_value_changed(self, slider, value_label, min_val, step):
        value = min_val + slider.value() * step
        value_label.setText(f'{value:.2f}')

    def reset_values(self):
        self.set_slider_value(self.k_slider, self.k_label, -10.0, 0.01, 2)
        self.set_slider_value(self.vg_slider, self.vg_label, -10.0, 0.01, 2)
        self.set_slider_value(self.amplitude_slider, self.amplitude_label, -10.0, 0.01, 2)
        self.set_slider_value(self.phase_velocity_slider, self.phase_velocity_label, -5.0, 0.1, 2)

    def set_slider_value(self, slider, label, min_val, step, value):
        slider.setValue(int((value - min_val) / step))
        label.setText(f'{value:.2f}')

    def wave_packet(self, k, x, t, amplitude, wave_type, phase_velocity):
        omega = k * phase_velocity
        if wave_type == "sinusoidalna":
            return amplitude * np.sin(k * x - omega * t)
        elif wave_type == "cosinusoidalna":
            return amplitude * np.cos(k * x - omega * t)

    def update_plot(self, frame):
        self.ax.clear()
        self.ax.set_xlabel('Odległość')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Animacja Paczek Falowych')

        wave_packet_sum = np.zeros_like(self.time)

        for k, group_velocity, amplitude, wave_type, phase_velocity in self.packets:
            wave_packet_sum += self.wave_packet(k, self.time, group_velocity * self.time[frame], amplitude, wave_type,
                                                phase_velocity)

        self.ax.plot(self.time, wave_packet_sum, label='Zsumowana Paczka Falowa')

        self.ax.legend(loc='upper right')
        self.ax.set_xlim(0, np.max(self.time))
        self.canvas.draw()

    def add_wave_packet(self):
        k = self.k_slider.value() * 0.01 - 10
        group_velocity = self.vg_slider.value() * 0.01 - 10
        amplitude = self.amplitude_slider.value() * 0.01 - 10
        phase_velocity = self.phase_velocity_slider.value() * 0.1 - 5
        wave_type = self.wave_type_combo.currentText()

        if self.invert_wave_checkbox.isChecked():
            amplitude = -amplitude

        if k is not None and group_velocity is not None and amplitude is not None and phase_velocity is not None:
            self.packets.append((k, group_velocity, amplitude, wave_type, phase_velocity))
            self.packet_list.addItem(
                f'k={k:.2f}, v_g={group_velocity:.2f}, A={amplitude:.2f}, Typ={wave_type}, v_f={phase_velocity:.2f}')
            self.update_plot(0)

    def remove_wave_packet(self):
        current_row = self.packet_list.currentRow()
        if current_row != -1:
            self.packet_list.takeItem(current_row)
            del self.packets[current_row]
            self.update_plot(0)

    def start_animation(self):
        if not self.packets:
            QMessageBox.warning(self, "Błąd", "Brak dodanych paczek falowych.")
            return

        interval = 50
        num_frames = len(self.time)

        def animate(frame):
            self.update_plot(frame)

        self.animation = FuncAnimation(self.canvas.figure, animate, frames=num_frames, interval=interval)

    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wave_packet_app = WavePacketApp()
    wave_packet_app.show()
    sys.exit(app.exec_())
