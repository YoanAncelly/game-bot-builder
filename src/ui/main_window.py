#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window for Game Bot Builder
"""

import os
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpacerItem, QSizePolicy,
    QTabWidget, QSplitter, QFileDialog, QMessageBox,
    QToolBar, QStatusBar, QMenu, QListWidget
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, Signal, Slot

from src.ui.workspace_panel import WorkspacePanel
from src.ui.image_recognition_panel import ImageRecognitionPanel
from src.ui.actions_panel import ActionsPanel
from src.ui.workflow_editor import WorkflowEditor
from src.modules.project import Project

logger = logging.getLogger("GameBotBuilder")


class MainWindow(QMainWindow):
    """Main window for the Game Bot Builder application."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.project = Project()
        
        # Set up the window
        self.setWindowTitle("Game Bot Builder")
        self.setMinimumSize(1200, 800)
        
        # Set up the UI
        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_statusbar()
        
        # Connect signals and slots
        self._connect_signals()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the main UI components."""
        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for main areas
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for workspace and tools
        self.left_panel = QTabWidget()
        self.workspace_panel = WorkspacePanel(self.project)
        self.image_recognition_panel = ImageRecognitionPanel(self.project)
        self.actions_panel = ActionsPanel(self.project)
        
        self.left_panel.addTab(self.workspace_panel, "Workspace")
        self.left_panel.addTab(self.image_recognition_panel, "Image Recognition")
        self.left_panel.addTab(self.actions_panel, "Actions")
        
        # Right panel for workflow editor
        self.workflow_editor = WorkflowEditor(self.project)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.workflow_editor)
        
        # Set initial sizes
        self.main_splitter.setSizes([300, 900])
        
        # Add the splitter to the main layout
        main_layout.addWidget(self.main_splitter)
    
    def _setup_menubar(self):
        """Set up the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New project action
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open project action
        open_action = QAction("&Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        # Save project action
        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # Save as action
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        # Undo action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        # Redo action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # Add buttons for common actions
        new_button = QAction("New", self)
        new_button.triggered.connect(self.new_project)
        toolbar.addAction(new_button)
        
        open_button = QAction("Open", self)
        open_button.triggered.connect(self.open_project)
        toolbar.addAction(open_button)
        
        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save_project)
        toolbar.addAction(save_button)
        
        toolbar.addSeparator()
        
        run_button = QAction("Run Bot", self)
        run_button.triggered.connect(self.run_bot)
        toolbar.addAction(run_button)
        
        stop_button = QAction("Stop Bot", self)
        stop_button.triggered.connect(self.stop_bot)
        toolbar.addAction(stop_button)
    
    def _setup_statusbar(self):
        """Set up the status bar."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect signals from panels and editors
        self.workflow_editor.status_message.connect(self.update_status)
        
        # Connect actions_updated signal from actions_panel to workflow_editor refresh
        self.actions_panel.actions_updated.connect(self.workflow_editor.refresh_scene)
    
    @Slot()
    def new_project(self):
        """Create a new project."""
        if self.project.is_modified:
            # Ask to save current project first
            reply = QMessageBox.question(
                self, "Save Changes",
                "Save changes to the current project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_project()
            elif reply == QMessageBox.Cancel:
                return
        
        # Create new project
        self.project = Project()
        self.workspace_panel.set_project(self.project)
        self.image_recognition_panel.set_project(self.project)
        self.actions_panel.set_project(self.project)
        self.workflow_editor.set_project(self.project)
        
        self.statusBar.showMessage("New project created")
    
    @Slot()
    def open_project(self):
        """Open an existing project."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Game Bot Builder Projects (*.gbb)"
        )
        
        if filename:
            try:
                self.project.load(filename)
                self.workspace_panel.set_project(self.project)
                self.image_recognition_panel.set_project(self.project)
                self.actions_panel.set_project(self.project)
                self.workflow_editor.set_project(self.project)
                self.statusBar.showMessage(f"Project loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
                logger.error(f"Failed to load project: {str(e)}")
    
    @Slot()
    def save_project(self):
        """Save the current project."""
        if not self.project.filename:
            self.save_project_as()
            return
        
        try:
            self.project.save()
            self.statusBar.showMessage(f"Project saved: {self.project.filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
            logger.error(f"Failed to save project: {str(e)}")
    
    @Slot()
    def save_project_as(self):
        """Save the current project with a new filename."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "Game Bot Builder Projects (*.gbb)"
        )
        
        if filename:
            try:
                if not filename.endswith(".gbb"):
                    filename += ".gbb"
                self.project.save(filename)
                self.statusBar.showMessage(f"Project saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
                logger.error(f"Failed to save project: {str(e)}")
    
    @Slot()
    def run_bot(self):
        """Run the current bot workflow."""
        try:
            self.project.run_workflow()
            self.statusBar.showMessage("Bot running...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run bot: {str(e)}")
            logger.error(f"Failed to run bot: {str(e)}")
    
    @Slot()
    def stop_bot(self):
        """Stop the currently running bot workflow."""
        try:
            self.project.stop_workflow()
            self.statusBar.showMessage("Bot stopped")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop bot: {str(e)}")
            logger.error(f"Failed to stop bot: {str(e)}")
    
    @Slot(str)
    def update_status(self, message):
        """Update the status bar with a message."""
        self.statusBar.showMessage(message)
    
    @Slot()
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Game Bot Builder",
            "Game Bot Builder\n\n"
            "A visual tool for creating game bots without coding.\n"
            "Design automation workflows by capturing screen elements\n"
            "and defining actions.\n\n"
            "Version 1.0.0"
        )
