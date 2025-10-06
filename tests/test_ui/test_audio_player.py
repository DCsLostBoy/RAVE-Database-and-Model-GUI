"""
Tests for the audio player widget.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from rave_gui.ui.widgets.audio_player import AudioPlayer


@pytest.fixture
def app():
    """Create application instance for testing."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


class TestAudioPlayer:
    """Tests for AudioPlayer widget."""
    
    def test_audio_player_creation(self, qtbot, app):
        """Test that audio player can be created."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        assert player.audio_data is None
        assert player.sample_rate is None
        assert player.current_file is None
        assert player.is_playing is False
        
    def test_initial_ui_state(self, qtbot, app):
        """Test initial UI state."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        assert player.play_btn.isEnabled() is False
        assert player.position_slider.isEnabled() is False
        assert player.time_label.text() == "0:00 / 0:00"
        
    def test_format_time(self, qtbot, app):
        """Test time formatting."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        assert player.format_time(0) == "0:00"
        assert player.format_time(65) == "1:05"
        assert player.format_time(125) == "2:05"
        assert player.format_time(3665) == "61:05"
        
    @patch('soundfile.read')
    def test_load_audio_success(self, mock_sf_read, qtbot, app):
        """Test successful audio loading."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Mock audio data
        mock_audio = np.random.randn(44100, 2)  # 1 second stereo
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            result = player.load_audio("/fake/path/test.wav")
            
        assert result is True
        assert player.audio_data is not None
        assert player.sample_rate == 44100
        assert player.play_btn.isEnabled() is True
        assert player.position_slider.isEnabled() is True
        
    def test_load_audio_nonexistent_file(self, qtbot, app):
        """Test loading nonexistent file."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        with patch.object(Path, 'exists', return_value=False):
            result = player.load_audio("/fake/path/nonexistent.wav")
            
        assert result is False
        assert player.audio_data is None
        
    @patch('soundfile.read')
    def test_load_audio_error(self, mock_sf_read, qtbot, app):
        """Test audio loading error handling."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        mock_sf_read.side_effect = Exception("Failed to load")
        
        with patch.object(Path, 'exists', return_value=True):
            result = player.load_audio("/fake/path/test.wav")
            
        assert result is False
        assert "Error loading" in player.file_label.text()
        
    @patch('soundfile.read')
    @patch('sounddevice.play')
    def test_start_playback(self, mock_sd_play, mock_sf_read, qtbot, app):
        """Test starting playback."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Load mock audio
        mock_audio = np.random.randn(44100, 2)
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            player.load_audio("/fake/path/test.wav")
            
        # Start playback
        player.start_playback()
        
        assert player.is_playing is True
        assert player.play_btn.text() == "Stop"
        mock_sd_play.assert_called_once()
        
    @patch('soundfile.read')
    @patch('sounddevice.play')
    @patch('sounddevice.stop')
    def test_stop_playback(self, mock_sd_stop, mock_sd_play, mock_sf_read, qtbot, app):
        """Test stopping playback."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Load and start playback
        mock_audio = np.random.randn(44100, 2)
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            player.load_audio("/fake/path/test.wav")
            
        player.start_playback()
        assert player.is_playing is True
        
        # Stop playback
        player.stop_playback()
        
        assert player.is_playing is False
        assert player.play_btn.text() == "Play"
        assert player.current_position == 0
        mock_sd_stop.assert_called_once()
        
    @patch('soundfile.read')
    @patch('sounddevice.play')
    def test_toggle_playback(self, mock_sd_play, mock_sf_read, qtbot, app):
        """Test toggling playback."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Load audio
        mock_audio = np.random.randn(44100, 2)
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            player.load_audio("/fake/path/test.wav")
            
        # First toggle - should start
        assert player.is_playing is False
        player.toggle_playback()
        assert player.is_playing is True
        
        # Second toggle - should stop
        with patch('sounddevice.stop'):
            player.toggle_playback()
            assert player.is_playing is False
            
    @patch('soundfile.read')
    def test_waveform_drawing(self, mock_sf_read, qtbot, app):
        """Test waveform visualization."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Load audio
        mock_audio = np.random.randn(44100, 2)
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            player.load_audio("/fake/path/test.wav")
            
        # Waveform should be drawn
        pixmap = player.waveform_label.pixmap()
        assert pixmap is not None
        assert not pixmap.isNull()
        
    def test_empty_waveform(self, qtbot, app):
        """Test empty waveform display."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Initial state should have empty waveform
        pixmap = player.waveform_label.pixmap()
        assert pixmap is not None
        assert not pixmap.isNull()
        
    def test_signals_exist(self, qtbot, app):
        """Test that player signals exist."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Check signals are defined
        assert hasattr(player, 'playback_started')
        assert hasattr(player, 'playback_stopped')
        
    @patch('soundfile.read')
    @patch('sounddevice.play')
    def test_playback_signals(self, mock_sd_play, mock_sf_read, qtbot, app):
        """Test that playback signals are emitted."""
        player = AudioPlayer()
        qtbot.addWidget(player)
        
        # Setup signal spies
        started_spy = Mock()
        stopped_spy = Mock()
        player.playback_started.connect(started_spy)
        player.playback_stopped.connect(stopped_spy)
        
        # Load audio
        mock_audio = np.random.randn(44100, 2)
        mock_sf_read.return_value = (mock_audio, 44100)
        
        with patch.object(Path, 'exists', return_value=True):
            player.load_audio("/fake/path/test.wav")
            
        # Start playback
        player.start_playback()
        started_spy.assert_called_once()
        
        # Stop playback
        with patch('sounddevice.stop'):
            player.stop_playback()
            stopped_spy.assert_called_once()
