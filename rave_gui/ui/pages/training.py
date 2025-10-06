"""
Training page - Configure and monitor model training.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QProgressBar, QTextEdit, QSplitter, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from rave_gui.ui.dialogs.new_training import NewTrainingWizard
from rave_gui.ui.widgets.metrics_plot import MetricsPlot
from rave_gui.backend.training import TrainingManager, TrainingProcess
from rave_gui.core.signals import AppSignals


class TrainingPage(QWidget):
    """Training page for configuring and monitoring model training."""
    
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db = db_connection
        self.training_manager = TrainingManager(db_connection)
        self.signals = AppSignals()
        self.active_training_widgets = {}  # experiment_id -> widget
        
        self.init_ui()
        self.connect_signals()
        self.load_experiments()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with title and new training button
        header_layout = QHBoxLayout()
        
        title = QLabel("Training")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.new_training_btn = QPushButton("New Training")
        self.new_training_btn.clicked.connect(self.start_new_training)
        header_layout.addWidget(self.new_training_btn)
        
        layout.addLayout(header_layout)
        
        # Split view: experiments list on left, details on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Experiments table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Training Experiments"))
        
        self.experiments_table = QTableWidget()
        self.experiments_table.setColumnCount(5)
        self.experiments_table.setHorizontalHeaderLabels([
            "Name", "Status", "Started", "Steps", "Actions"
        ])
        self.experiments_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.experiments_table.itemSelectionChanged.connect(
            self.on_experiment_selected
        )
        left_layout.addWidget(self.experiments_table)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Training details and metrics
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Training info group
        info_group = QGroupBox("Training Information")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Select an experiment to view details")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.progress_bar)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Metrics plot
        self.metrics_plot = MetricsPlot()
        right_layout.addWidget(self.metrics_plot)
        
        # Training log viewer
        log_group = QGroupBox("Training Log")
        log_layout = QVBoxLayout()
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMaximumHeight(150)
        log_layout.addWidget(self.log_viewer)
        
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        self.selected_experiment_id = None
        
    def connect_signals(self):
        """Connect application signals."""
        self.signals.training_started.connect(self.on_training_started)
        self.signals.training_progress.connect(self.on_training_progress)
        self.signals.training_completed.connect(self.on_training_completed)
        self.signals.training_stopped.connect(self.on_training_stopped)
    
    def start_new_training(self):
        """Open the new training wizard."""
        wizard = NewTrainingWizard(self.db, self)
        
        if wizard.exec():
            # Get configuration from wizard
            config = wizard.get_config()
            
            # Create experiment in database
            experiment_id = self.training_manager.start_training(config)
            
            # Create and start training process
            training_process = TrainingProcess(config)
            
            # Connect training process signals
            training_process.output.connect(
                lambda line, eid=experiment_id: self.on_training_output(eid, line)
            )
            training_process.metrics_update.connect(
                lambda metrics, eid=experiment_id: self.on_metrics_update(eid, metrics)
            )
            training_process.step_update.connect(
                lambda step, total, eid=experiment_id: self.on_step_update(eid, step, total)
            )
            training_process.finished.connect(
                lambda success, msg, eid=experiment_id: self.on_training_finished(eid, success, msg)
            )
            
            # Register process with manager
            self.training_manager.register_process(experiment_id, training_process)
            
            # Start the training
            training_process.start()
            
            # Emit signal and reload
            self.signals.training_started.emit(experiment_id, config['name'])
            self.load_experiments()
    
    def load_experiments(self):
        """Load experiments from database."""
        experiments = self.training_manager.list_experiments()
        
        self.experiments_table.setRowCount(len(experiments))
        
        for i, exp in enumerate(experiments):
            # Name
            self.experiments_table.setItem(i, 0, QTableWidgetItem(exp['name']))
            
            # Status
            status_item = QTableWidgetItem(exp['status'])
            self.experiments_table.setItem(i, 1, status_item)
            
            # Started time
            if exp.get('started_at'):
                started = exp['started_at'].split('T')[0]  # Just date
                self.experiments_table.setItem(i, 2, QTableWidgetItem(started))
            
            # Steps (from metrics)
            metrics = exp.get('metrics', {})
            if metrics and 'step' in metrics:
                step_text = f"{int(metrics['step']):,}"
                self.experiments_table.setItem(i, 3, QTableWidgetItem(step_text))
            
            # Actions (stop button for running experiments)
            if exp['status'] == 'running':
                stop_btn = QPushButton("Stop")
                stop_btn.clicked.connect(
                    lambda checked, eid=exp['id']: self.stop_training(eid)
                )
                self.experiments_table.setCellWidget(i, 4, stop_btn)
        
        self.experiments_table.resizeColumnsToContents()
    
    def on_experiment_selected(self):
        """Handle experiment selection."""
        rows = self.experiments_table.selectedItems()
        if not rows:
            return
        
        row = self.experiments_table.currentRow()
        experiments = self.training_manager.list_experiments()
        
        if row < len(experiments):
            experiment = experiments[row]
            self.selected_experiment_id = experiment['id']
            self.display_experiment_details(experiment)
    
    def display_experiment_details(self, experiment):
        """Display details of selected experiment."""
        info = f"Name: {experiment['name']}\n"
        info += f"Status: {experiment['status']}\n"
        info += f"Started: {experiment.get('started_at', 'N/A')}\n"
        
        if experiment.get('completed_at'):
            info += f"Completed: {experiment['completed_at']}\n"
        
        metrics = experiment.get('metrics', {})
        if metrics:
            if 'step' in metrics:
                info += f"\nCurrent Step: {int(metrics['step']):,}\n"
            if 'loss' in metrics:
                info += f"Loss: {metrics['loss']:.4f}\n"
        
        self.info_label.setText(info)
        
        # Show progress bar if running
        if experiment['status'] == 'running':
            self.progress_bar.setVisible(True)
            if metrics and 'step' in metrics:
                config = experiment.get('config', {})
                max_steps = config.get('max_steps', 500000)
                progress = int((metrics['step'] / max_steps) * 100)
                self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
        
        # Update metrics plot
        self.metrics_plot.clear()
        if metrics:
            self.metrics_plot.update_metrics(metrics)
    
    def stop_training(self, experiment_id):
        """Stop a training run."""
        if self.training_manager.stop_training(experiment_id):
            self.signals.training_stopped.emit(experiment_id)
            self.load_experiments()
    
    def on_training_started(self, experiment_id, name):
        """Handle training started signal."""
        self.log_viewer.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training started: {name}")
    
    def on_training_progress(self, experiment_id, step, metrics):
        """Handle training progress signal."""
        # Update metrics in database
        self.training_manager.update_training_metrics(experiment_id, metrics)
        
        # Update display if this is the selected experiment
        if experiment_id == self.selected_experiment_id:
            experiment = self.training_manager.get_experiment(experiment_id)
            if experiment:
                self.display_experiment_details(experiment)
    
    def on_training_output(self, experiment_id, line):
        """Handle training output line."""
        if experiment_id == self.selected_experiment_id:
            self.log_viewer.append(line)
            # Auto-scroll to bottom
            scrollbar = self.log_viewer.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def on_metrics_update(self, experiment_id, metrics):
        """Handle metrics update from training process."""
        # Update in database
        current_metrics = self.training_manager.get_training_metrics(experiment_id)
        current_metrics.update(metrics)
        self.training_manager.update_training_metrics(experiment_id, current_metrics)
        
        # Update plot if this is selected experiment
        if experiment_id == self.selected_experiment_id:
            self.metrics_plot.update_metrics(metrics)
        
        # Emit progress signal
        step = int(metrics.get('step', 0))
        self.signals.training_progress.emit(experiment_id, step, metrics)
    
    def on_step_update(self, experiment_id, step, total):
        """Handle step update."""
        if experiment_id == self.selected_experiment_id:
            progress = int((step / total) * 100) if total > 0 else 0
            self.progress_bar.setValue(progress)
    
    def on_training_finished(self, experiment_id, success, message):
        """Handle training completion."""
        status = 'completed' if success else 'failed'
        self.training_manager.update_experiment_status(
            experiment_id, 
            status, 
            datetime.now().isoformat()
        )
        self.training_manager.unregister_process(experiment_id)
        
        self.signals.training_completed.emit(experiment_id, success)
        
        self.log_viewer.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Training {status}: {message}"
        )
        
        self.load_experiments()
    
    def on_training_completed(self, experiment_id, success):
        """Handle training completed signal."""
        pass  # Already handled in on_training_finished
    
    def on_training_stopped(self, experiment_id):
        """Handle training stopped signal."""
        self.log_viewer.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Training stopped"
        )
