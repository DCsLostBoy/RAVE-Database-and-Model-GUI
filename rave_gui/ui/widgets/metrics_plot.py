"""
Metrics plotting widget for displaying training metrics.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT


class MetricsPlot(QWidget):
    """Widget for plotting training metrics using matplotlib."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_history = {
            'step': [],
            'loss': [],
            'val_loss': [],
            'lr': []
        }
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Create subplots
        self.ax_loss = self.figure.add_subplot(2, 1, 1)
        self.ax_lr = self.figure.add_subplot(2, 1, 2)
        
        # Configure loss plot
        self.ax_loss.set_xlabel('Step')
        self.ax_loss.set_ylabel('Loss')
        self.ax_loss.set_title('Training Loss')
        self.ax_loss.grid(True, alpha=0.3)
        
        # Configure learning rate plot
        self.ax_lr.set_xlabel('Step')
        self.ax_lr.set_ylabel('Learning Rate')
        self.ax_lr.set_title('Learning Rate Schedule')
        self.ax_lr.grid(True, alpha=0.3)
        self.ax_lr.set_yscale('log')
        
        self.figure.tight_layout()
        
    def update_metrics(self, metrics: dict):
        """Update the plot with new metrics.
        
        Args:
            metrics: Dictionary containing metrics (step, loss, val_loss, lr, etc.)
        """
        # Append new metrics to history
        if 'step' in metrics:
            self.metrics_history['step'].append(metrics['step'])
        
        for key in ['loss', 'val_loss', 'lr']:
            if key in metrics:
                self.metrics_history[key].append(metrics[key])
            elif len(self.metrics_history[key]) < len(self.metrics_history['step']):
                # Pad with None if metric not present
                self.metrics_history[key].append(None)
        
        # Update plots
        self._update_plots()
    
    def _update_plots(self):
        """Redraw the plots with current metrics."""
        if not self.metrics_history['step']:
            return
        
        steps = self.metrics_history['step']
        
        # Clear and update loss plot
        self.ax_loss.clear()
        self.ax_loss.set_xlabel('Step')
        self.ax_loss.set_ylabel('Loss')
        self.ax_loss.set_title('Training Loss')
        self.ax_loss.grid(True, alpha=0.3)
        
        if any(self.metrics_history['loss']):
            loss_steps = [s for s, l in zip(steps, self.metrics_history['loss']) if l is not None]
            loss_values = [l for l in self.metrics_history['loss'] if l is not None]
            if loss_values:
                self.ax_loss.plot(loss_steps, loss_values, label='Training Loss', color='blue')
        
        if any(self.metrics_history['val_loss']):
            val_steps = [s for s, v in zip(steps, self.metrics_history['val_loss']) if v is not None]
            val_values = [v for v in self.metrics_history['val_loss'] if v is not None]
            if val_values:
                self.ax_loss.plot(val_steps, val_values, label='Validation Loss', 
                                 color='orange', linestyle='--')
        
        # Add legend after plotting data
        self.ax_loss.legend()
        
        # Clear and update learning rate plot
        self.ax_lr.clear()
        self.ax_lr.set_xlabel('Step')
        self.ax_lr.set_ylabel('Learning Rate')
        self.ax_lr.set_title('Learning Rate Schedule')
        self.ax_lr.grid(True, alpha=0.3)
        self.ax_lr.set_yscale('log')
        
        if any(self.metrics_history['lr']):
            lr_steps = [s for s, l in zip(steps, self.metrics_history['lr']) if l is not None]
            lr_values = [l for l in self.metrics_history['lr'] if l is not None]
            if lr_values:
                self.ax_lr.plot(lr_steps, lr_values, color='green')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
        """Clear all metrics history and plots."""
        self.metrics_history = {
            'step': [],
            'loss': [],
            'val_loss': [],
            'lr': []
        }
        self.ax_loss.clear()
        self.ax_lr.clear()
        self.canvas.draw()
