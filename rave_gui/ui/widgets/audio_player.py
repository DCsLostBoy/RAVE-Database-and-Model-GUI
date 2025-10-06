"""
Audio player widget for previewing audio files.
"""
from pathlib import Path
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
import soundfile as sf
import sounddevice as sd


class AudioPlayer(QWidget):
    """Audio player widget with play/pause controls and waveform display."""
    
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.current_file = None
        self.is_playing = False
        self.current_position = 0
        self.stream = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # File info label
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.file_label)
        
        # Waveform display area
        self.waveform_label = QLabel()
        self.waveform_label.setMinimumHeight(100)
        self.waveform_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.waveform_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.draw_empty_waveform()
        layout.addWidget(self.waveform_label)
        
        # Controls
        controls = QHBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_playback)
        controls.addWidget(self.play_btn)
        
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderPressed.connect(self.on_slider_pressed)
        self.position_slider.sliderReleased.connect(self.on_slider_released)
        controls.addWidget(self.position_slider)
        
        self.time_label = QLabel("0:00 / 0:00")
        controls.addWidget(self.time_label)
        
        layout.addLayout(controls)
        
    def draw_empty_waveform(self):
        """Draw empty waveform placeholder."""
        pixmap = QPixmap(400, 100)
        pixmap.fill(QColor(255, 255, 255))
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "No audio loaded")
        painter.end()
        self.waveform_label.setPixmap(pixmap)
        
    def draw_waveform(self):
        """Draw the waveform visualization."""
        if self.audio_data is None:
            return
            
        width = self.waveform_label.width()
        height = self.waveform_label.height()
        
        if width < 10 or height < 10:
            width, height = 400, 100
            
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(255, 255, 255))
        painter = QPainter(pixmap)
        
        # Draw waveform
        painter.setPen(QPen(QColor(50, 150, 250), 1))
        
        # Get mono signal for visualization
        if len(self.audio_data.shape) > 1:
            signal = np.mean(self.audio_data, axis=1)
        else:
            signal = self.audio_data
            
        # Downsample for visualization
        samples_per_pixel = max(1, len(signal) // width)
        downsampled = signal[::samples_per_pixel]
        
        # Normalize to display height
        if len(downsampled) > 0:
            max_val = np.max(np.abs(downsampled))
            if max_val > 0:
                downsampled = downsampled / max_val * (height / 2 - 10)
        
        # Draw waveform
        center_y = height // 2
        for i in range(min(len(downsampled) - 1, width)):
            x1 = i
            y1 = int(center_y - downsampled[i])
            x2 = i + 1
            y2 = int(center_y - downsampled[min(i + 1, len(downsampled) - 1)])
            painter.drawLine(x1, y1, x2, y2)
        
        # Draw center line
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(0, center_y, width, center_y)
        
        painter.end()
        self.waveform_label.setPixmap(pixmap)
        
    def load_audio(self, file_path):
        """Load an audio file for playback."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
                
            # Stop any current playback
            self.stop_playback()
            
            # Load audio file
            self.audio_data, self.sample_rate = sf.read(str(file_path))
            self.current_file = file_path
            self.current_position = 0
            
            # Update UI
            self.file_label.setText(f"{file_path.name} ({self.sample_rate} Hz, {self.audio_data.shape})")
            self.play_btn.setEnabled(True)
            self.position_slider.setEnabled(True)
            self.position_slider.setMaximum(len(self.audio_data))
            self.position_slider.setValue(0)
            
            # Update time label
            duration = len(self.audio_data) / self.sample_rate
            self.time_label.setText(f"0:00 / {self.format_time(duration)}")
            
            # Draw waveform
            self.draw_waveform()
            
            return True
        except Exception as e:
            self.file_label.setText(f"Error loading: {str(e)}")
            return False
            
    def format_time(self, seconds):
        """Format time in seconds to MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
        
    def toggle_playback(self):
        """Toggle audio playback."""
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
            
    def start_playback(self):
        """Start audio playback."""
        if self.audio_data is None:
            return
            
        try:
            self.is_playing = True
            self.play_btn.setText("Stop")
            self.playback_started.emit()
            
            # Start from current position
            start_frame = self.current_position
            audio_segment = self.audio_data[start_frame:]
            
            # Play audio
            sd.play(audio_segment, self.sample_rate)
            self.timer.start(50)  # Update position every 50ms
            
        except Exception as e:
            self.file_label.setText(f"Playback error: {str(e)}")
            self.stop_playback()
            
    def stop_playback(self):
        """Stop audio playback."""
        if self.is_playing:
            sd.stop()
            self.timer.stop()
            self.is_playing = False
            self.play_btn.setText("Play")
            self.current_position = 0
            self.position_slider.setValue(0)
            self.playback_stopped.emit()
            
            if self.audio_data is not None:
                duration = len(self.audio_data) / self.sample_rate
                self.time_label.setText(f"0:00 / {self.format_time(duration)}")
                
    def update_position(self):
        """Update playback position."""
        if not self.is_playing or self.audio_data is None:
            return
            
        # Check if playback finished
        if not sd.get_stream().active:
            self.stop_playback()
            return
            
        # Update position (estimate based on time)
        self.current_position = min(
            self.current_position + int(self.sample_rate * 0.05),
            len(self.audio_data)
        )
        self.position_slider.setValue(self.current_position)
        
        # Update time label
        current_time = self.current_position / self.sample_rate
        duration = len(self.audio_data) / self.sample_rate
        self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(duration)}")
        
    def on_slider_pressed(self):
        """Handle slider press - pause playback."""
        if self.is_playing:
            self.timer.stop()
            
    def on_slider_released(self):
        """Handle slider release - seek to position."""
        if self.audio_data is None:
            return
            
        self.current_position = self.position_slider.value()
        
        if self.is_playing:
            # Restart playback from new position
            sd.stop()
            start_frame = self.current_position
            audio_segment = self.audio_data[start_frame:]
            sd.play(audio_segment, self.sample_rate)
            self.timer.start(50)
        else:
            # Just update time label
            current_time = self.current_position / self.sample_rate
            duration = len(self.audio_data) / self.sample_rate
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(duration)}")
