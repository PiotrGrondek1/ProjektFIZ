import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QListWidget, QMessageBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class WavePacketApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animacja Pakietu Falowego")
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
        self.ax.set_title('Animacja Pakietu Falowego')

        self.add_packet_button = QPushButton('Dodaj Pakiet Falowy')
        self.add_packet_button.clicked.connect(self.add_wave_packet)
        self.layout.addWidget(self.add_packet_button)

        self.remove_packet_button = QPushButton('Usuń Pakiet Falowy')
        self.remove_packet_button.clicked.connect(self.remove_wave_packet)
        self.layout.addWidget(self.remove_packet_button)

        self.start_animation_button = QPushButton('Rozpocznij Animację')
        self.start_animation_button.clicked.connect(self.start_animation)
        self.layout.addWidget(self.start_animation_button)

        self.stop_animation_button = QPushButton('Zatrzymaj Animację')
        self.stop_animation_button.clicked.connect(self.stop_animation)
        self.layout.addWidget(self.stop_animation_button)

        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setMinimum(-1000)
        self.k_slider.setMaximum(1000)
        self.k_slider.setValue(500)
        self.k_slider.setTickPosition(QSlider.TicksBelow)
        self.k_slider.setTickInterval(1)
        self.k_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Liczba falowa (k):'))
        self.layout.addWidget(self.k_slider)

        self.vg_slider = QSlider(Qt.Horizontal)
        self.vg_slider.setMinimum(-1000)
        self.vg_slider.setMaximum(1000)
        self.vg_slider.setValue(500)
        self.vg_slider.setTickPosition(QSlider.TicksBelow)
        self.vg_slider.setTickInterval(1)
        self.vg_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Prędkość grupowa (v_g):'))
        self.layout.addWidget(self.vg_slider)

        self.vp_slider = QSlider(Qt.Horizontal)
        self.vp_slider.setMinimum(-1000)
        self.vp_slider.setMaximum(1000)
        self.vp_slider.setValue(500)
        self.vp_slider.setTickPosition(QSlider.TicksBelow)
        self.vp_slider.setTickInterval(1)
        self.vp_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(QLabel('Prędkość fazowa (v_p):'))
        self.layout.addWidget(self.vp_slider)

        self.packet_list = QListWidget()
        self.layout.addWidget(QLabel('Lista Pakietów Falowych:'))
        self.layout.addWidget(self.packet_list)

        self.packets = []
        self.time = np.linspace(0, 10, 1000)  # Skrócony czas symulacji do 10 sekund
        self.animation = None

    def wave_packet(self, k, x, t, group_velocity, phase_velocity):
        envelope = np.exp(-0.1 * (x - group_velocity * t)**2)  # Gaussowska obwiednia
        carrier = np.cos(k * (x - phase_velocity * t))
        return envelope * carrier

    def update_plot(self, frame):
        self.ax.clear()
        self.ax.set_xlabel('Odległość')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Animacja Pakietu Falowego')

        x = np.linspace(0, 20, 2000)
        for k, group_velocity, phase_velocity in self.packets:
            wave_packet_sum = self.wave_packet(k, x, self.time[frame], group_velocity, phase_velocity)
            self.ax.plot(x, wave_packet_sum, label=f'k={k}, v_g={group_velocity}, v_p={phase_velocity}')

        self.ax.legend(loc='upper right')
        self.ax.set_xlim(0, np.max(x))
        self.ax.set_ylim(-3, 3)  # Ustalony poziom amplitudy, aby uniknąć rozjeżdżania się wykresu

        self.canvas.draw()

    def add_wave_packet(self):
        k = self.k_slider.value() / 100
        group_velocity = self.vg_slider.value() / 100
        phase_velocity = self.vp_slider.value() / 100

        if k is not None and group_velocity is not None and phase_velocity is not None:
            self.packets.append((k, group_velocity, phase_velocity))
            self.packet_list.addItem(f'k={k}, v_g={group_velocity}, v_p={phase_velocity}')
            self.update_plot(0)

    def remove_wave_packet(self):
        current_row = self.packet_list.currentRow()
        if current_row != -1:
            self.packet_list.takeItem(current_row)
            del self.packets[current_row]
            self.update_plot(0)

    def start_animation(self):
        if not self.packets:
            QMessageBox.warning(self, "Błąd", "Nie dodano żadnych pakietów falowych.")
            return

        interval = 20  # Zmniejszony interwał między klatkami, aby przyspieszyć animację
        num_frames = len(self.time)

        def animate(frame):
            self.update_plot(frame)

        self.animation = FuncAnimation(self.canvas.figure, animate, frames=num_frames, interval=interval, repeat=True)

    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()

    def slider_value_changed(self):
        k = self.k_slider.value() / 100
        group_velocity = self.vg_slider.value() / 100
        phase_velocity = self.vp_slider.value() / 100
        self.k_slider.setToolTip(f'Liczba falowa (k): {k}')
        self.vg_slider.setToolTip(f'Prędkość grupowa (v_g): {group_velocity}')
        self.vp_slider.setToolTip(f'Prędkość fazowa (v_p): {phase_velocity}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wave_packet_app = WavePacketApp()
    wave_packet_app.show()
    sys.exit(app.exec_())
