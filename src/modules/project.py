#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project class for Game Bot Builder

Handles saving, loading, and managing bot projects.
"""

import os
import json
import jsonpickle
import logging
from datetime import datetime
from PySide6.QtCore import QObject, Signal

from src.modules.workflow import Workflow
from src.modules.workspace import Workspace

logger = logging.getLogger("GameBotBuilder")


class Project(QObject):
    """Represents a bot building project."""
    
    # Signals
    project_modified = Signal()
    project_saved = Signal(str)  # Filename
    project_loaded = Signal(str)  # Filename
    
    def __init__(self):
        super().__init__()
        
        # Project properties
        self.name = "New Project"
        self.description = ""
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.filename = None
        self.is_modified = False
        
        # Project components
        self.workspace = Workspace()
        self.workflows = []  # List of Workflow objects
        self.images = {}  # Dict of image_id -> {"path": str, "description": str}
        self.settings = {}
        
        # Create a default workflow
        self.add_workflow(Workflow("Main Workflow"))
        
        logger.info("New project initialized")
    
    def add_workflow(self, workflow):
        """Add a workflow to the project.
        
        Args:
            workflow: The Workflow object to add
        """
        self.workflows.append(workflow)
        self.mark_modified()
        logger.info(f"Added workflow: {workflow.name}")
    
    def remove_workflow(self, workflow_id):
        """Remove a workflow from the project.
        
        Args:
            workflow_id: The ID of the workflow to remove
        """
        for i, workflow in enumerate(self.workflows):
            if workflow.id == workflow_id:
                del self.workflows[i]
                self.mark_modified()
                logger.info(f"Removed workflow: {workflow.name}")
                return True
        return False
    
    def get_workflow(self, workflow_id):
        """Get a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow to get
            
        Returns:
            The Workflow object, or None if not found
        """
        for workflow in self.workflows:
            if workflow.id == workflow_id:
                return workflow
        return None
    
    def add_image(self, image_path, description=""):
        """Add an image to the project.
        
        Args:
            image_path: Path to the image file
            description: Optional description of the image
            
        Returns:
            The ID of the newly added image
        """
        import uuid
        image_id = str(uuid.uuid4())
        
        # If image_path is not absolute, make it relative to project directory
        if not os.path.isabs(image_path) and self.filename:
            project_dir = os.path.dirname(self.filename)
            image_path = os.path.join(project_dir, image_path)
        
        self.images[image_id] = {
            "path": image_path,
            "description": description
        }
        
        self.mark_modified()
        logger.info(f"Added image: {image_path}")
        return image_id
    
    def remove_image(self, image_id):
        """Remove an image from the project.
        
        Args:
            image_id: The ID of the image to remove
            
        Returns:
            True if the image was removed, False otherwise
        """
        if image_id in self.images:
            del self.images[image_id]
            self.mark_modified()
            logger.info(f"Removed image: {image_id}")
            return True
        return False
    
    def mark_modified(self):
        """Mark the project as modified."""
        self.is_modified = True
        self.modified_at = datetime.now()
        self.project_modified.emit()
    
    def run_workflow(self, workflow_id=None):
        """Run a workflow from the project.
        
        Args:
            workflow_id: The ID of the workflow to run. If None, runs the first workflow.
        """
        if workflow_id is None and self.workflows:
            workflow = self.workflows[0]
        else:
            workflow = self.get_workflow(workflow_id)
        
        if workflow:
            logger.info(f"Running workflow: {workflow.name}")
            return workflow.execute(self)
        else:
            logger.error("No workflow to run")
            raise ValueError("No workflow to run")
    
    def stop_workflow(self):
        """Stop all running workflows."""
        for workflow in self.workflows:
            if workflow.is_running:
                workflow.stop()
        
        logger.info("All workflows stopped")
    
    def save(self, filename=None):
        """Save the project to a file.
        
        Args:
            filename: The file to save to. If None, uses the current filename.
        """
        if filename:
            self.filename = filename
        
        if not self.filename:
            raise ValueError("No filename specified")
        
        # Prepare project data
        project_data = {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "modified_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Add serialized project components
        project_data["workspace"] = jsonpickle.encode(self.workspace)
        project_data["workflows"] = jsonpickle.encode(self.workflows)
        project_data["images"] = self.images
        project_data["settings"] = self.settings
        
        # Create project directory if it doesn't exist
        project_dir = os.path.dirname(self.filename)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        # Write to file
        with open(self.filename, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        self.is_modified = False
        self.project_saved.emit(self.filename)
        logger.info(f"Project saved: {self.filename}")
    
    def load(self, filename):
        """Load a project from a file.
        
        Args:
            filename: The file to load from
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Project file not found: {filename}")
        
        with open(filename, 'r') as f:
            project_data = json.load(f)
        
        # Load project properties
        self.name = project_data.get("name", "Unnamed Project")
        self.description = project_data.get("description", "")
        self.created_at = datetime.fromisoformat(project_data.get("created_at", datetime.now().isoformat()))
        self.modified_at = datetime.fromisoformat(project_data.get("modified_at", datetime.now().isoformat()))
        self.filename = filename
        
        # Load project components
        self.workspace = jsonpickle.decode(project_data.get("workspace", jsonpickle.encode(Workspace())))
        self.workflows = jsonpickle.decode(project_data.get("workflows", jsonpickle.encode([])))
        self.images = project_data.get("images", {})
        self.settings = project_data.get("settings", {})
        
        self.is_modified = False
        self.project_loaded.emit(self.filename)
        logger.info(f"Project loaded: {self.filename}")
