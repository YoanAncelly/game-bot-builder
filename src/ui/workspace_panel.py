#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Workspace Panel for Game Bot Builder

Provides UI controls for screen capture and image recognition.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, Slot, QRect
from PySide6.QtGui import QPixmap, QImage

from src.modules.project import Project


class WorkspacePanel(QWidget):
    """Panel for managing screen captures and image recognition."""
    
    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Screen Capture Section
        capture_group = QWidget()
        capture_layout = QVBoxLayout(capture_group)
        
        # Capture controls
        capture_controls = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Screen")
        self.capture_btn.clicked.connect(self.capture_screen)
        capture_controls.addWidget(self.capture_btn)
        
        self.capture_region_btn = QPushButton("Capture Region")
        self.capture_region_btn.clicked.connect(self.capture_region)
        capture_controls.addWidget(self.capture_region_btn)
        
        capture_layout.addLayout(capture_controls)
        
        # Region selection
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("X:"))
        self.region_x = QSpinBox()
        self.region_x.setRange(0, 9999)
        region_layout.addWidget(self.region_x)
        
        region_layout.addWidget(QLabel("Y:"))
        self.region_y = QSpinBox()
        self.region_y.setRange(0, 9999)
        region_layout.addWidget(self.region_y)
        
        region_layout.addWidget(QLabel("Width:"))
        self.region_width = QSpinBox()
        self.region_width.setRange(1, 9999)
        self.region_width.setValue(100)
        region_layout.addWidget(self.region_width)
        
        region_layout.addWidget(QLabel("Height:"))
        self.region_height = QSpinBox()
        self.region_height.setRange(1, 9999)
        self.region_height.setValue(100)
        region_layout.addWidget(self.region_height)
        
        capture_layout.addLayout(region_layout)
        
        # Preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setStyleSheet("border: 1px solid gray")
        capture_layout.addWidget(self.preview_label)
        
        layout.addWidget(capture_group)
        
        # Captured Images List
        self.images_list = QListWidget()
        self.images_list.itemSelectionChanged.connect(self._on_image_selected)
        layout.addWidget(QLabel("Captured Images:"))
        layout.addWidget(self.images_list)
        
        # Image controls
        image_controls = QHBoxLayout()
        self.add_image_btn = QPushButton("Add Image")
        self.add_image_btn.clicked.connect(self.add_image)
        image_controls.addWidget(self.add_image_btn)
        
        self.remove_image_btn = QPushButton("Remove Image")
        self.remove_image_btn.clicked.connect(self.remove_image)
        image_controls.addWidget(self.remove_image_btn)
        
        layout.addLayout(image_controls)
        
        # Connect project signals
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_images_list)
        
        # Initial refresh
        self._refresh_images_list()
        
    def set_project(self, project: Project):
        """Set the current project.
        
        Args:
            project: The Project instance to use
        """
        if self.project:
            self.project.project_loaded.disconnect(self._on_project_loaded)
            self.project.project_modified.disconnect(self._refresh_images_list)
            
        self.project = project
        
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_images_list)
        
        self._refresh_images_list()
        
    @Slot()
    def capture_screen(self):
        """Capture the entire screen."""
        try:
            filepath = self.project.workspace.capture_screen()
            self._show_preview(filepath)
            self._refresh_images_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to capture screen: {str(e)}")
            
    @Slot()
    def capture_region(self):
        """Capture a specific region of the screen."""
        try:
            region = (
                self.region_x.value(),
                self.region_y.value(),
                self.region_width.value(),
                self.region_height.value()
            )
            
            filepath = self.project.workspace.capture_screen(region)
            self._show_preview(filepath)
            self._refresh_images_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to capture region: {str(e)}")
            
    @Slot()
    def add_image(self):
        """Add an external image to the project."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if filepath:
            try:
                description = os.path.basename(filepath)
                self.project.add_image(filepath, description)
                self._refresh_images_list()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add image: {str(e)}")
                
    @Slot()
    def remove_image(self):
        """Remove the selected image from the project."""
        current_item = self.images_list.currentItem()
        if not current_item:
            return
            
        image_id = current_item.data(Qt.UserRole)
        if not image_id:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this image?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.project.remove_image(image_id)
                self._refresh_images_list()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove image: {str(e)}")
                
    def _show_preview(self, image_path: str):
        """Show an image preview.
        
        Args:
            image_path: Path to the image to preview
        """
        try:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to show preview: {str(e)}")
            
    def _refresh_images_list(self):
        """Refresh the list of images."""
        self.images_list.clear()
        
        for image_id, image_data in self.project.images.items():
            item = QListWidgetItem(image_data["description"])
            item.setData(Qt.UserRole, image_id)
            self.images_list.addItem(item)
            
    @Slot()
    def _on_image_selected(self):
        """Handle image selection in the list."""
        current_item = self.images_list.currentItem()
        if not current_item:
            return
            
        image_id = current_item.data(Qt.UserRole)
        if not image_id or image_id not in self.project.images:
            return
            
        image_path = self.project.images[image_id]["path"]
        self._show_preview(image_path)
        
    @Slot(str)
    def _on_project_loaded(self, filename: str):
        """Handle project loaded event.
        
        Args:
            filename: Path to the loaded project file
        """
        self._refresh_images_list()
