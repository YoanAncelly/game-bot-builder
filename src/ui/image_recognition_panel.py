#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Recognition Panel for Game Bot Builder

Provides UI controls for configuring and testing image recognition.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QMessageBox, QListWidget,
    QListWidgetItem, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, Slot, QRect
from PySide6.QtGui import QPixmap

from src.modules.project import Project


class ImageRecognitionPanel(QWidget):
    """Panel for configuring image recognition settings."""
    
    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Image Selection
        layout.addWidget(QLabel("Target Image:"))
        self.image_list = QListWidget()
        self.image_list.itemSelectionChanged.connect(self._on_image_selected)
        layout.addWidget(self.image_list)
        
        # Preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setStyleSheet("border: 1px solid gray")
        layout.addWidget(self.preview_label)
        
        # Recognition Settings
        settings_layout = QVBoxLayout()
        
        # Threshold setting
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Match Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(80)  # Default 0.8
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_value = QDoubleSpinBox()
        self.threshold_value.setRange(0.0, 1.0)
        self.threshold_value.setSingleStep(0.05)
        self.threshold_value.setValue(0.8)
        self.threshold_value.valueChanged.connect(self._on_threshold_value_changed)
        threshold_layout.addWidget(self.threshold_value)
        settings_layout.addLayout(threshold_layout)
        
        # Match Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Match Mode:"))
        self.match_mode = QComboBox()
        self.match_mode.addItems([
            "TM_CCOEFF_NORMED",
            "TM_CCORR_NORMED",
            "TM_SQDIFF_NORMED"
        ])
        mode_layout.addWidget(self.match_mode)
        settings_layout.addLayout(mode_layout)
        
        # Multi-scale matching settings
        multi_scale_group = QGroupBox("Multi-Scale Matching")
        multi_scale_layout = QVBoxLayout(multi_scale_group)
        
        # Enable multi-scale checkbox
        self.use_multi_scale_cb = QCheckBox("Enable Multi-Scale Matching")
        multi_scale_layout.addWidget(self.use_multi_scale_cb)
        
        # Scale range and steps
        scale_form = QFormLayout()
        
        # Min scale
        self.min_scale = QDoubleSpinBox()
        self.min_scale.setRange(0.1, 1.0)
        self.min_scale.setSingleStep(0.05)
        self.min_scale.setValue(0.8)
        scale_form.addRow("Min Scale:", self.min_scale)
        
        # Max scale
        self.max_scale = QDoubleSpinBox()
        self.max_scale.setRange(1.0, 2.0)
        self.max_scale.setSingleStep(0.05)
        self.max_scale.setValue(1.2)
        scale_form.addRow("Max Scale:", self.max_scale)
        
        # Scale steps
        self.scale_steps = QSpinBox()
        self.scale_steps.setRange(1, 20)
        self.scale_steps.setValue(5)
        scale_form.addRow("Scale Steps:", self.scale_steps)
        
        multi_scale_layout.addLayout(scale_form)
        settings_layout.addWidget(multi_scale_group)
        
        # Options
        options_layout = QVBoxLayout()
        self.grayscale_cb = QCheckBox("Convert to Grayscale")
        self.grayscale_cb.setChecked(True)
        options_layout.addWidget(self.grayscale_cb)
        
        self.highlight_matches_cb = QCheckBox("Highlight Matches")
        self.highlight_matches_cb.setChecked(True)
        options_layout.addWidget(self.highlight_matches_cb)
        
        settings_layout.addLayout(options_layout)
        
        layout.addLayout(settings_layout)
        
        # Test Controls
        test_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Recognition")
        self.test_btn.clicked.connect(self.test_recognition)
        test_layout.addWidget(self.test_btn)
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        test_layout.addWidget(self.clear_btn)
        
        layout.addLayout(test_layout)
        
        # Results
        layout.addWidget(QLabel("Recognition Results:"))
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        # Connect project signals
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_image_list)
        
        # Initial refresh
        self._refresh_image_list()
        
    def set_project(self, project: Project):
        """Set the current project.
        
        Args:
            project: The Project instance to use
        """
        if self.project:
            self.project.project_loaded.disconnect(self._on_project_loaded)
            self.project.project_modified.disconnect(self._refresh_image_list)
            
        self.project = project
        
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_image_list)
        
        self._refresh_image_list()
        
    @Slot()
    def test_recognition(self):
        """Test image recognition with current settings."""
        current_item = self.image_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an image to test")
            return
            
        image_id = current_item.data(Qt.UserRole)
        if not image_id or image_id not in self.project.images:
            return
            
        try:
            # Take a screenshot
            screen_path = self.project.workspace.capture_screen()
            
            # Get template path
            template_path = self.project.images[image_id]["path"]
            
            # Get multi-scale settings
            use_multi_scale = self.use_multi_scale_cb.isChecked()
            scale_range = (self.min_scale.value(), self.max_scale.value())
            scale_steps = self.scale_steps.value()
            
            # Perform recognition
            matches = self.project.workspace.find_template(
                template_path,
                screen_path,
                threshold=self.threshold_value.value(),
                use_multi_scale=use_multi_scale,
                scale_range=scale_range,
                scale_steps=scale_steps
            )
            
            # Clear previous results
            self.results_list.clear()
            
            # Show results
            if matches:
                for i, rect in enumerate(matches, 1):
                    item = QListWidgetItem(
                        f"Match {i}: ({rect.x()}, {rect.y()}) - "
                        f"{rect.width()}x{rect.height()}"
                    )
                    self.results_list.addItem(item)
                    
                    # Highlight match if enabled
                    if self.highlight_matches_cb.isChecked():
                        self.project.workspace.highlight_region(rect)
            else:
                self.results_list.addItem("No matches found")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Recognition failed: {str(e)}")
            
    @Slot()
    def clear_results(self):
        """Clear recognition results."""
        self.results_list.clear()
        
    def _refresh_image_list(self):
        """Refresh the list of available images."""
        self.image_list.clear()
        
        for image_id, image_data in self.project.images.items():
            item = QListWidgetItem(image_data["description"])
            item.setData(Qt.UserRole, image_id)
            self.image_list.addItem(item)
            
    @Slot()
    def _on_image_selected(self):
        """Handle image selection in the list."""
        current_item = self.image_list.currentItem()
        if not current_item:
            return
            
        image_id = current_item.data(Qt.UserRole)
        if not image_id or image_id not in self.project.images:
            return
            
        # Update the preview
        image_path = self.project.images[image_id]["path"]
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            # Scale down if too large
            if pixmap.width() > 320 or pixmap.height() > 240:
                pixmap = pixmap.scaled(320, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("Preview not available")
            
    @Slot(int)
    def _on_threshold_changed(self, value):
        """Handle threshold slider change."""
        # Update the value spinbox without triggering its valueChanged signal
        self.threshold_value.blockSignals(True)
        self.threshold_value.setValue(value / 100.0)
        self.threshold_value.blockSignals(False)
        
    @Slot(float)
    def _on_threshold_value_changed(self, value):
        """Handle threshold value change."""
        # Update the slider without triggering its valueChanged signal
        self.threshold_slider.blockSignals(True)
        self.threshold_slider.setValue(int(value * 100))
        self.threshold_slider.blockSignals(False)
        
    @Slot()
    def _on_project_loaded(self):
        """Handle project loaded signal."""
        self._refresh_image_list()
