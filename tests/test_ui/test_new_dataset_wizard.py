"""
Tests for the dataset creation wizard.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from rave_gui.ui.dialogs.new_dataset import (
    NewDatasetWizard,
    IntroPage,
    InputFilesPage,
    ParametersPage,
    PreprocessingPage
)


@pytest.fixture
def app():
    """Create application instance for testing."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


class TestNewDatasetWizard:
    """Tests for NewDatasetWizard."""
    
    def test_wizard_creation(self, qtbot, app):
        """Test that wizard can be created."""
        wizard = NewDatasetWizard()
        qtbot.addWidget(wizard)
        
        assert wizard.windowTitle() == "Create New Dataset"
        assert wizard.minimumWidth() == 800
        assert wizard.minimumHeight() == 600
        
    def test_wizard_pages(self, qtbot, app):
        """Test that all pages are added."""
        wizard = NewDatasetWizard()
        qtbot.addWidget(wizard)
        
        # Should have 4 pages: intro, files, params, processing
        page_ids = wizard.pageIds()
        assert len(page_ids) == 4
        
    def test_get_audio_files(self, qtbot, app):
        """Test getting audio files from wizard."""
        wizard = NewDatasetWizard()
        qtbot.addWidget(wizard)
        
        # Initially empty
        files = wizard.get_audio_files()
        assert files == []
        
    def test_get_dataset_config(self, qtbot, app):
        """Test getting dataset config from wizard."""
        wizard = NewDatasetWizard()
        qtbot.addWidget(wizard)
        
        config = wizard.get_dataset_config()
        assert isinstance(config, dict)
        assert 'name' in config
        assert 'sample_rate' in config


class TestIntroPage:
    """Tests for IntroPage."""
    
    def test_intro_page_creation(self, qtbot, app):
        """Test intro page creation."""
        page = IntroPage()
        qtbot.addWidget(page)
        
        assert page.title() == "Create New Dataset"
        assert "preprocess" in page.subTitle().lower()


class TestInputFilesPage:
    """Tests for InputFilesPage."""
    
    def test_input_files_page_creation(self, qtbot, app):
        """Test input files page creation."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        assert page.title() == "Select Audio Files"
        assert page.audio_files == []
        
    def test_audio_extensions(self, qtbot, app):
        """Test supported audio extensions."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        expected_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.aif', '.aiff', '.opus', '.aac']
        assert page.AUDIO_EXTENSIONS == expected_extensions
        
    def test_add_audio_file(self, qtbot, app):
        """Test adding an audio file."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        # Mock file
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test.wav")
            
        assert len(page.audio_files) == 1
        assert page.audio_files[0] == "/fake/path/test.wav"
        
    def test_add_duplicate_file(self, qtbot, app):
        """Test that duplicate files are not added."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test.wav")
            page.add_audio_file("/fake/path/test.wav")
            
        assert len(page.audio_files) == 1
        
    def test_add_invalid_file(self, qtbot, app):
        """Test that non-audio files are rejected."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test.txt")
            
        assert len(page.audio_files) == 0
        
    def test_clear_files(self, qtbot, app):
        """Test clearing all files."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test.wav")
            
        assert len(page.audio_files) == 1
        
        page.clear_files()
        assert len(page.audio_files) == 0
        
    def test_is_complete(self, qtbot, app):
        """Test page completion validation."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        # Empty page is not complete
        assert not page.isComplete()
        
        # Page with files is complete
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test.wav")
            
        assert page.isComplete()
        
    def test_get_audio_files(self, qtbot, app):
        """Test getting audio files list."""
        page = InputFilesPage()
        qtbot.addWidget(page)
        
        with patch.object(Path, 'exists', return_value=True):
            page.add_audio_file("/fake/path/test1.wav")
            page.add_audio_file("/fake/path/test2.wav")
            
        files = page.get_audio_files()
        assert len(files) == 2
        assert "/fake/path/test1.wav" in files
        assert "/fake/path/test2.wav" in files


class TestParametersPage:
    """Tests for ParametersPage."""
    
    def test_parameters_page_creation(self, qtbot, app):
        """Test parameters page creation."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        assert page.title() == "Dataset Parameters"
        
    def test_default_values(self, qtbot, app):
        """Test default parameter values."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        assert page.sample_rate_spin.value() == 44100
        assert page.channels_spin.value() == 1
        assert page.signal_length_spin.value() == 65536
        assert page.dyndb_check.isChecked() is True
        assert page.lazy_check.isChecked() is False
        
    def test_is_complete_empty_name(self, qtbot, app):
        """Test that empty name makes page incomplete."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        page.name_edit.setText("")
        page.output_path_edit.setText("/some/path")
        
        assert not page.isComplete()
        
    def test_is_complete_valid(self, qtbot, app):
        """Test that valid inputs make page complete."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        page.name_edit.setText("my_dataset")
        page.output_path_edit.setText("/some/path")
        
        assert page.isComplete()
        
    def test_invalid_name_validation(self, qtbot, app):
        """Test validation of invalid dataset names."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        # Name with special characters (not allowed)
        page.name_edit.setText("my@dataset!")
        assert not page.isComplete()
        
        # Valid name
        page.name_edit.setText("my_dataset-01")
        page.output_path_edit.setText("/some/path")
        assert page.isComplete()
        
    def test_get_config(self, qtbot, app):
        """Test getting configuration dictionary."""
        page = ParametersPage()
        qtbot.addWidget(page)
        
        page.name_edit.setText("test_dataset")
        page.output_path_edit.setText("/output/path")
        page.sample_rate_spin.setValue(48000)
        page.channels_spin.setValue(2)
        page.signal_length_spin.setValue(32768)
        page.lazy_check.setChecked(True)
        page.dyndb_check.setChecked(False)
        
        config = page.get_config()
        
        assert config['name'] == "test_dataset"
        assert config['output_path'] == "/output/path"
        assert config['sample_rate'] == 48000
        assert config['channels'] == 2
        assert config['signal_length'] == 32768
        assert config['lazy'] is True
        assert config['dyndb'] is False


class TestPreprocessingPage:
    """Tests for PreprocessingPage."""
    
    def test_preprocessing_page_creation(self, qtbot, app):
        """Test preprocessing page creation."""
        page = PreprocessingPage()
        qtbot.addWidget(page)
        
        assert page.title() == "Preprocessing"
        assert page.is_processing is False
        
    def test_initial_state(self, qtbot, app):
        """Test initial UI state."""
        page = PreprocessingPage()
        qtbot.addWidget(page)
        
        assert page.progress_bar.value() == 0
        assert page.start_btn.isEnabled() is True
        assert page.cancel_btn.isEnabled() is False
        
    def test_update_progress(self, qtbot, app):
        """Test progress update."""
        page = PreprocessingPage()
        qtbot.addWidget(page)
        
        page.update_progress(50, 5, 10)
        
        assert page.progress_bar.value() == 50
        assert "5 / 10" in page.file_counter_label.text()
        
    def test_log_append(self, qtbot, app):
        """Test log message appending."""
        page = PreprocessingPage()
        qtbot.addWidget(page)
        
        page.log_append("Test message")
        
        assert "Test message" in page.log_viewer.toPlainText()
        
    def test_is_complete(self, qtbot, app):
        """Test page completion status."""
        page = PreprocessingPage()
        qtbot.addWidget(page)
        
        # Not processing - complete
        page.is_processing = False
        assert page.isComplete() is True
        
        # Processing - not complete
        page.is_processing = True
        assert page.isComplete() is False
