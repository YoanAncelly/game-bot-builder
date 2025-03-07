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
    QListWidgetItem, QGroupBox, QFormLayout, QScrollArea,
    QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QRect
from PySide6.QtGui import QPixmap
import numpy as np
import cv2

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
        layout.setSpacing(10)  # Add spacing between elements
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins around the entire layout
        
        # === Image Selection Section ===
        self.image_selection_group = QGroupBox("Image Selection")
        image_selection_layout = QVBoxLayout(self.image_selection_group)
        
        self.image_list = QListWidget()
        self.image_list.itemSelectionChanged.connect(self._on_image_selected)
        self.image_list.setMinimumHeight(100)  # Ensure reasonable height
        self.image_list.setMaximumHeight(150)  # But not too tall
        image_selection_layout.addWidget(self.image_list)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(240, 180)  # Reduced size
        self.preview_label.setMaximumSize(320, 240)  # Capped maximum size
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        preview_layout.addWidget(self.preview_label)
        image_selection_layout.addLayout(preview_layout)
        
        layout.addWidget(self.image_selection_group)
        
        # Create a scroll area for all the settings
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Container widget for the scroll area
        settings_container = QWidget()
        settings_scroll_layout = QVBoxLayout(settings_container)
        settings_scroll_layout.setSpacing(15)  # More spacing between settings groups
        
        # === Target Analysis Section ===
        self.analysis_group = QGroupBox("Target Analysis")
        analysis_layout = QVBoxLayout(self.analysis_group)
        analysis_layout.setSpacing(8)
        
        self.analyze_btn = QPushButton("Analyze Target")
        self.analyze_btn.clicked.connect(self._analyze_target)
        analysis_layout.addWidget(self.analyze_btn)
        
        # Use a QTextEdit instead of QLabel for better text display
        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)  # Make it read-only
        self.analysis_results.setMinimumHeight(80)  # Ensure enough height to display results
        self.analysis_results.setMaximumHeight(120)  # But not too tall
        self.analysis_results.setStyleSheet("background-color: white; color: #222222; padding: 5px; border: 1px solid #cccccc;")
        self.analysis_results.setHtml("<p style='color: #666666;'>Select an image and click Analyze Target</p>")
        analysis_layout.addWidget(self.analysis_results)
        
        settings_scroll_layout.addWidget(self.analysis_group)
        
        # === Basic Recognition Settings ===
        self.basic_settings_group = QGroupBox("Basic Settings")
        basic_settings_layout = QFormLayout(self.basic_settings_group)
        basic_settings_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        basic_settings_layout.setSpacing(10)
        
        # Threshold setting with a more compact layout
        threshold_widget = QWidget()
        threshold_layout = QHBoxLayout(threshold_widget)
        threshold_layout.setContentsMargins(0, 0, 0, 0)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(80)  # Default 0.8
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.threshold_slider, 3)  # Give more space to slider
        
        self.threshold_value = QDoubleSpinBox()
        self.threshold_value.setRange(0.0, 1.0)
        self.threshold_value.setSingleStep(0.05)
        self.threshold_value.setValue(0.8)
        self.threshold_value.setMaximumWidth(70)  # Make spinner more compact
        self.threshold_value.valueChanged.connect(self._on_threshold_value_changed)
        threshold_layout.addWidget(self.threshold_value, 1)
        
        basic_settings_layout.addRow("Match Threshold:", threshold_widget)
        
        # Match Mode
        self.match_mode = QComboBox()
        self.match_mode.addItems([
            "TM_CCOEFF_NORMED",
            "TM_CCORR_NORMED",
            "TM_SQDIFF_NORMED"
        ])
        basic_settings_layout.addRow("Match Mode:", self.match_mode)
        
        # Options
        options_widget = QWidget()
        options_layout = QHBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(20)  # More spacing between checkboxes
        
        self.grayscale_cb = QCheckBox("Convert to Grayscale")
        self.grayscale_cb.setChecked(True)
        options_layout.addWidget(self.grayscale_cb)
        
        self.highlight_matches_cb = QCheckBox("Highlight Matches")
        self.highlight_matches_cb.setChecked(True)
        options_layout.addWidget(self.highlight_matches_cb)
        
        basic_settings_layout.addRow("", options_widget)
        
        settings_scroll_layout.addWidget(self.basic_settings_group)
        
        # === Advanced Recognition Settings (in collapsible sections) ===
        # Color filtering settings
        self.color_group = QGroupBox("Color Filtering")
        self.color_group.setCheckable(True)
        self.color_group.setChecked(False)  # Unchecked by default
        self.color_group.toggled.connect(self._on_color_filtering_toggled)
        color_layout = QVBoxLayout(self.color_group)
        color_layout.setSpacing(8)
        
        # Color range settings
        self.color_range_widget = QWidget()
        color_range_layout = QVBoxLayout(self.color_range_widget)
        color_range_layout.setContentsMargins(0, 0, 0, 0)
        
        self.use_auto_color_cb = QCheckBox("Auto-detect Color Range")
        self.use_auto_color_cb.setChecked(True)
        color_range_layout.addWidget(self.use_auto_color_cb)
        
        # Custom color range settings
        self.custom_color_widget = QWidget()
        custom_color_layout = QFormLayout(self.custom_color_widget)
        custom_color_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        custom_color_layout.setSpacing(8)
        
        # Lower bound RGB - in a more compact row
        lower_rgb_widget = QWidget()
        lower_rgb_layout = QHBoxLayout(lower_rgb_widget)
        lower_rgb_layout.setContentsMargins(0, 0, 0, 0)
        lower_rgb_layout.setSpacing(5)
        
        lower_rgb_layout.addWidget(QLabel("R:"))
        self.lower_r = QSpinBox()
        self.lower_r.setRange(0, 255)
        self.lower_r.setMaximumWidth(60)
        lower_rgb_layout.addWidget(self.lower_r)
        
        lower_rgb_layout.addWidget(QLabel("G:"))
        self.lower_g = QSpinBox()
        self.lower_g.setRange(0, 255)
        self.lower_g.setMaximumWidth(60)
        lower_rgb_layout.addWidget(self.lower_g)
        
        lower_rgb_layout.addWidget(QLabel("B:"))
        self.lower_b = QSpinBox()
        self.lower_b.setRange(0, 255)
        self.lower_b.setMaximumWidth(60)
        lower_rgb_layout.addWidget(self.lower_b)
        
        custom_color_layout.addRow("Lower RGB:", lower_rgb_widget)
        
        # Upper bound RGB - in a more compact row
        upper_rgb_widget = QWidget()
        upper_rgb_layout = QHBoxLayout(upper_rgb_widget)
        upper_rgb_layout.setContentsMargins(0, 0, 0, 0)
        upper_rgb_layout.setSpacing(5)
        
        upper_rgb_layout.addWidget(QLabel("R:"))
        self.upper_r = QSpinBox()
        self.upper_r.setRange(0, 255)
        self.upper_r.setValue(255)
        self.upper_r.setMaximumWidth(60)
        upper_rgb_layout.addWidget(self.upper_r)
        
        upper_rgb_layout.addWidget(QLabel("G:"))
        self.upper_g = QSpinBox()
        self.upper_g.setRange(0, 255)
        self.upper_g.setValue(255)
        self.upper_g.setMaximumWidth(60)
        upper_rgb_layout.addWidget(self.upper_g)
        
        upper_rgb_layout.addWidget(QLabel("B:"))
        self.upper_b = QSpinBox()
        self.upper_b.setRange(0, 255)
        self.upper_b.setValue(255)
        self.upper_b.setMaximumWidth(60)
        upper_rgb_layout.addWidget(self.upper_b)
        
        custom_color_layout.addRow("Upper RGB:", upper_rgb_widget)
        
        self.custom_color_widget.setLayout(custom_color_layout)
        color_range_layout.addWidget(self.custom_color_widget)
        
        self.color_range_widget.setLayout(color_range_layout)
        color_layout.addWidget(self.color_range_widget)
        
        # Connect toggle for custom color settings
        self.use_auto_color_cb.toggled.connect(lambda checked: self.custom_color_widget.setVisible(not checked))
        self.custom_color_widget.setVisible(False)  # Hide by default
        
        settings_scroll_layout.addWidget(self.color_group)
        
        # Shape matching settings
        self.shape_group = QGroupBox("Shape Matching")
        self.shape_group.setCheckable(True)
        self.shape_group.setChecked(False)  # Unchecked by default
        self.shape_group.toggled.connect(self._on_shape_matching_toggled)
        shape_layout = QVBoxLayout(self.shape_group)
        shape_layout.setSpacing(8)
        
        # Shape threshold
        self.shape_threshold_widget = QWidget()
        shape_threshold_layout = QFormLayout(self.shape_threshold_widget)
        shape_threshold_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        threshold_slider_widget = QWidget()
        threshold_slider_layout = QHBoxLayout(threshold_slider_widget)
        threshold_slider_layout.setContentsMargins(0, 0, 0, 0)
        
        self.shape_threshold_slider = QSlider(Qt.Horizontal)
        self.shape_threshold_slider.setRange(0, 100)
        self.shape_threshold_slider.setValue(70)  # Default 0.7
        self.shape_threshold_slider.valueChanged.connect(self._on_shape_threshold_changed)
        threshold_slider_layout.addWidget(self.shape_threshold_slider, 3)
        
        self.shape_threshold_value = QDoubleSpinBox()
        self.shape_threshold_value.setRange(0.0, 1.0)
        self.shape_threshold_value.setSingleStep(0.05)
        self.shape_threshold_value.setValue(0.7)
        self.shape_threshold_value.setMaximumWidth(70)
        self.shape_threshold_value.valueChanged.connect(self._on_shape_threshold_value_changed)
        threshold_slider_layout.addWidget(self.shape_threshold_value, 1)
        
        shape_threshold_layout.addRow("Shape Threshold:", threshold_slider_widget)
        
        shape_layout.addWidget(self.shape_threshold_widget)
        settings_scroll_layout.addWidget(self.shape_group)
        
        # Multi-scale matching settings
        self.multi_scale_group = QGroupBox("Multi-Scale Matching")
        self.multi_scale_group.setCheckable(True)
        self.multi_scale_group.setChecked(False)  # Unchecked by default
        self.multi_scale_group.toggled.connect(self._on_multi_scale_toggled)
        multi_scale_layout = QVBoxLayout(self.multi_scale_group)
        multi_scale_layout.setSpacing(8)
        
        # Scale range and steps
        self.scale_widget = QWidget()
        scale_form = QFormLayout(self.scale_widget)
        scale_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        scale_form.setSpacing(8)
        
        # Min scale
        self.min_scale = QDoubleSpinBox()
        self.min_scale.setRange(0.1, 1.0)
        self.min_scale.setSingleStep(0.05)
        self.min_scale.setValue(0.8)
        self.min_scale.setMaximumWidth(70)
        scale_form.addRow("Min Scale:", self.min_scale)
        
        # Max scale
        self.max_scale = QDoubleSpinBox()
        self.max_scale.setRange(1.0, 2.0)
        self.max_scale.setSingleStep(0.05)
        self.max_scale.setValue(1.2)
        self.max_scale.setMaximumWidth(70)
        scale_form.addRow("Max Scale:", self.max_scale)
        
        # Scale steps
        self.scale_steps = QSpinBox()
        self.scale_steps.setRange(1, 20)
        self.scale_steps.setValue(5)
        self.scale_steps.setMaximumWidth(70)
        scale_form.addRow("Scale Steps:", self.scale_steps)
        
        multi_scale_layout.addWidget(self.scale_widget)
        settings_scroll_layout.addWidget(self.multi_scale_group)
        
        # === Action Buttons ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.test_btn = QPushButton("Test Recognition")
        self.test_btn.clicked.connect(self.test_recognition)
        self.test_btn.setMinimumHeight(30)  # Taller button
        button_layout.addWidget(self.test_btn)
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setMinimumHeight(30)  # Taller button
        button_layout.addWidget(self.clear_btn)
        
        settings_scroll_layout.addLayout(button_layout)
        
        # === Results Section ===
        self.results_group = QGroupBox("Recognition Results")
        results_layout = QVBoxLayout(self.results_group)
        
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(100)  # Ensure it has space
        self.results_list.setAlternatingRowColors(True)  # Better visual distinction
        results_layout.addWidget(self.results_list)
        
        settings_scroll_layout.addWidget(self.results_group)
        
        # Finish setting up scroll area
        settings_container.setLayout(settings_scroll_layout)
        settings_scroll.setWidget(settings_container)
        layout.addWidget(settings_scroll, 1)  # Give scroll area all remaining space
        
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
            
            # Get color filtering settings
            use_color_filtering = self.color_group.isChecked()
            color_range = None
            if use_color_filtering and not self.use_auto_color_cb.isChecked():
                lower_rgb = (self.lower_r.value(), self.lower_g.value(), self.lower_b.value())
                upper_rgb = (self.upper_r.value(), self.upper_g.value(), self.upper_b.value())
                color_range = (lower_rgb, upper_rgb)
            
            # Get shape matching settings
            match_shape = self.shape_group.isChecked()
            shape_threshold = self.shape_threshold_value.value()
            
            # Get multi-scale settings
            use_multi_scale = self.multi_scale_group.isChecked()
            scale_range = (self.min_scale.value(), self.max_scale.value())
            scale_steps = self.scale_steps.value()
            
            # Perform recognition
            matches = self.project.workspace.find_template(
                template_path,
                screen_path,
                threshold=self.threshold_value.value(),
                use_multi_scale=use_multi_scale,
                scale_range=scale_range,
                scale_steps=scale_steps,
                use_color_filtering=use_color_filtering,
                color_range=color_range,
                match_shape=match_shape,
                shape_threshold=shape_threshold
            )
            
            # Update results list
            self.results_list.clear()
            if matches:
                for i, rect in enumerate(matches):
                    item = QListWidgetItem(f"Match #{i+1}: ({rect.x()}, {rect.y()}, {rect.width()}, {rect.height()})")
                    self.results_list.addItem(item)
                    
                    # Highlight match if enabled
                    if self.highlight_matches_cb.isChecked():
                        self.project.workspace.highlight_region(rect)
            else:
                self.results_list.addItem("No matches found")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Recognition test failed: {str(e)}")
            
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
        
    @Slot(bool)
    def _on_color_filtering_toggled(self, checked):
        """Handle color filtering toggle."""
        self.color_range_widget.setVisible(checked)
        
    @Slot(bool)
    def _on_shape_matching_toggled(self, checked):
        """Handle shape matching toggle."""
        self.shape_threshold_widget.setVisible(checked)
    
    @Slot(bool)
    def _on_multi_scale_toggled(self, checked):
        """Handle multi-scale toggle."""
        self.scale_widget.setVisible(checked)
    
    @Slot()
    def _on_shape_threshold_changed(self, value):
        """Handle shape threshold slider change."""
        threshold = value / 100.0
        self.shape_threshold_value.blockSignals(True)
        self.shape_threshold_value.setValue(threshold)
        self.shape_threshold_value.blockSignals(False)
    
    @Slot()
    def _on_shape_threshold_value_changed(self, value):
        """Handle shape threshold spinbox change."""
        self.shape_threshold_slider.blockSignals(True)
        self.shape_threshold_slider.setValue(int(value * 100))
        self.shape_threshold_slider.blockSignals(False)
        
    @Slot()
    def _analyze_target(self):
        """Analyze the selected target image to extract properties."""
        current_item = self.image_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an image to analyze")
            return
            
        image_id = current_item.data(Qt.UserRole)
        if not image_id or image_id not in self.project.images:
            return
            
        try:
            # Get template path
            template_path = self.project.images[image_id]["path"]
            
            # Perform analysis
            analysis = self.project.workspace.analyze_target_image(template_path)
            
            # Display analysis results
            avg_color_bgr = analysis["avg_color_bgr"]
            shape_info = analysis["shape"]
            
            result_text = f"<p style='color: #222222; margin: 5px 0;'><b>Color:</b> RGB({int(avg_color_bgr[2])}, {int(avg_color_bgr[1])}, {int(avg_color_bgr[0])})</p>"
            if shape_info:
                result_text += f"<p style='color: #222222; margin: 5px 0;'><b>Shape:</b> {shape_info['type'].capitalize()}</p>"
                result_text += f"<p style='color: #222222; margin: 5px 0;'><b>Circularity:</b> {shape_info['circularity']:.2f}</p>"
            
            self.analysis_results.setHtml(result_text)
            
            # Set color filter values to match the target if auto color is checked
            if self.use_auto_color_cb.isChecked():
                # Calculate color range based on the average color
                # This creates a range of +/- 30 for each channel (adjust as needed)
                margin = 30  # Adjust this value as needed
                lower_r = max(0, avg_color_bgr[2] - margin)
                lower_g = max(0, avg_color_bgr[1] - margin)
                lower_b = max(0, avg_color_bgr[0] - margin)
                upper_r = min(255, avg_color_bgr[2] + margin)
                upper_g = min(255, avg_color_bgr[1] + margin)
                upper_b = min(255, avg_color_bgr[0] + margin)
                
                # Update the color range UI controls
                self.lower_r.setValue(int(lower_r))
                self.lower_g.setValue(int(lower_g))
                self.lower_b.setValue(int(lower_b))
                self.upper_r.setValue(int(upper_r))
                self.upper_g.setValue(int(upper_g))
                self.upper_b.setValue(int(upper_b))
                
                # Enable color filtering
                self.color_group.setChecked(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
