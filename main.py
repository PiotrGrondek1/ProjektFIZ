import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, Animation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QMessageBox, QSlider, QComboBox, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class WavePacketInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dodaj Paczkę Falową")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("Podaj liczbę falową (k)")
        self.layout.addWidget(self.k_input)

        self.group_velocity_input = QLineEdit()
        self.group_velocity_input.setPlaceholderText("Podaj prędkość grupową")
        self.layout.addWidget(self.group_velocity_input)

        self.accept_button = QPushButton("Dodaj Paczkę Falową")
        self.accept_button.clicked.connect(self.accept)
        self.layout.addWidget(self.accept_button)

    def get_k_group_velocity(self):
        k_text = self.k_input.text().strip()
        group_velocity_text = self.group_velocity_input.text().strip()

        if k_text and group_velocity_text:
            try:
                k = float(k_text)
                group_velocity = float(group_velocity_text)
                return k, group_velocity
            except ValueError:
                pass

        return None, None


class WavePacketApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animacja Paczek Falowych")
        self.setGeometry(100, 100, 1200, 800)  # Powiększenie okna programu

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

        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setMinimum(1)
        self.k_slider.setMaximum(1000)  # Zwiększenie liczby punktów na suwaku
        self.k_slider.setValue(500)
        self.k_slider.setTickPosition(QSlider.TicksBelow)
        self.k_slider.setTickInterval(1)
        self.k_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Liczba falowa (k):'))
        self.layout.addWidget(self.k_slider)

        self.vg_slider = QSlider(Qt.Horizontal)
        self.vg_slider.setMinimum(1)
        self.vg_slider.setMaximum(1000)  # Zwiększenie liczby punktów na suwaku
        self.vg_slider.setValue(500)
        self.vg_slider.setTickPosition(QSlider.TicksBelow)
        self.vg_slider.setTickInterval(1)
        self.vg_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Prędkość grupowa:'))
        self.layout.addWidget(self.vg_slider)

        self.amplitude_slider = QSlider(Qt.Horizontal)
        self.amplitude_slider.setMinimum(1)
        self.amplitude_slider.setMaximum(1000)  # Zwiększenie liczby punktów na suwaku
        self.amplitude_slider.setValue(500)
        self.amplitude_slider.setTickPosition(QSlider.TicksBelow)
        self.amplitude_slider.setTickInterval(1)
        self.amplitude_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Amplituda:'))
        self.layout.addWidget(self.amplitude_slider)

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

        self.packets = []  # Lista przechowująca informacje o paczkach falowych
        self.time = np.linspace(0, 20, 2000)  # Rozszerzony czas dla większej ilości fal
        self.animation = None

    def wave_packet(self, k, x, t, amplitude, wave_type):
        omega = k  # Prędkość fazowa przyjęta jako 1
        if wave_type == "sinusoidalna":
            return amplitude * np.sin(k * x - omega * t)
        elif wave_type == "cosinusoidalna":
            return amplitude * np.cos(k * x - omega * t)

    def update_plot(self, frame):
        self.ax.clear()
        self.ax.set_xlabel('Odległość')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Animacja Paczek Falowych')

        # Initialize the wave packet sum with zeros
        wave_packet_sum = np.zeros_like(self.time)

        # Sum up all wave packets
        for k, group_velocity, amplitude, wave_type in self.packets:
            wave_packet_sum += self.wave_packet(k, self.time, group_velocity * self.time[frame], amplitude, wave_type)

        # Plot the resultant wave packet
        self.ax.plot(self.time, wave_packet_sum, label='Zsumowana Paczka Falowa')

        self.ax.legend(loc='upper right')  # Przeniesienie legendy do górnego prawego rogu
        self.ax.set_xlim(0, np.max(self.time))  # Ustawienie szerokości osi x na maksymalną wartość czasu
        self.canvas.draw()

    def add_wave_packet(self):
        k = self.k_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        group_velocity = self.vg_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        amplitude = self.amplitude_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        wave_type = self.wave_type_combo.currentText()

        if self.invert_wave_checkbox.isChecked():
            amplitude = -amplitude

        if k is not None and group_velocity is not None and amplitude is not None:
            self.packets.append((k, group_velocity, amplitude, wave_type))
            self.packet_list.addItem(f'k={k}, v_g={group_velocity}, A={amplitude}, Typ={wave_type}')
            self.update_plot(0)  # Aktualizacja wykresu dla nowej paczki falowej

    def remove_wave_packet(self):
        current_row = self.packet_list.currentRow()
        if current_row != -1:
            self.packet_list.takeItem(current_row)
            del self.packets[current_row]
            self.update_plot(0)  # Aktualizacja wykresu po usunięciu paczki falowej

    def start_animation(self):
        if not self.packets:
            QMessageBox.warning(self, "Błąd", "Brak dodanych paczek falowych.")
            return

        interval = 50  # Interwał między klatkami w milisekundach
        num_frames = len(self.time)

        def animate(frame):
            self.update_plot(frame)

        self.animation = FuncAnimation(self.canvas.figure, animate, frames=num_frames, interval=interval)

    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()

    def slider_value_changed(self):
        k = self.k_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        group_velocity = self.vg_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        amplitude = self.amplitude_slider.value() / 100  # Zmniejszenie kwantu na suwakach do 0,01
        self.k_slider.setToolTip(f'Liczba falowa (k): {k}')
        self.vg_slider.setToolTip(f'Prędkość grupowa: {group_velocity}')
        self.amplitude_slider.setToolTip(f'Amplituda: {amplitude}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wave_packet_app = WavePacketApp()
    wave_packet_app.show()
    sys.exit(app.exec_())
