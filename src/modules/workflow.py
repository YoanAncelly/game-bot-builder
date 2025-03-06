#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Workflow module for Game Bot Builder

Handles the creation and execution of automation workflows.
"""

import uuid
import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from PySide6.QtCore import QObject, Signal, QThread

logger = logging.getLogger("GameBotBuilder")


class ActionType(Enum):
    """Types of actions that can be performed in a workflow."""
    FIND_IMAGE = "find_image"
    CLICK = "click"
    MOVE_MOUSE = "move_mouse"
    WAIT = "wait"
    KEYBOARD_INPUT = "keyboard_input"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class Action:
    """Represents a single action in a workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ActionType = ActionType.FIND_IMAGE
    name: str = "Unnamed Action"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    next_action_id: Optional[str] = None
    condition_true_id: Optional[str] = None  # For conditional actions
    condition_false_id: Optional[str] = None  # For conditional actions
    enabled: bool = True


class WorkflowExecutor(QThread):
    """Executes workflow actions in a separate thread."""
    
    # Signals
    action_started = Signal(str)  # Action ID
    action_completed = Signal(str)  # Action ID
    action_failed = Signal(str, str)  # Action ID, Error message
    workflow_completed = Signal()
    workflow_stopped = Signal()
    
    def __init__(self, workflow, project):
        super().__init__()
        self.workflow = workflow
        self.project = project
        self.stop_flag = False
        
    def run(self):
        """Execute the workflow."""
        try:
            current_action = self.workflow.get_start_action()
            
            while current_action and not self.stop_flag:
                self.action_started.emit(current_action.id)
                
                try:
                    next_action_id = self._execute_action(current_action)
                    self.action_completed.emit(current_action.id)
                    
                    if next_action_id:
                        current_action = self.workflow.get_action(next_action_id)
                    else:
                        current_action = None
                        
                except Exception as e:
                    error_msg = f"Action failed: {str(e)}"
                    logger.error(error_msg)
                    self.action_failed.emit(current_action.id, error_msg)
                    break
                
                time.sleep(0.1)  # Small delay between actions
            
            if self.stop_flag:
                self.workflow_stopped.emit()
            else:
                self.workflow_completed.emit()
                
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            
    def stop(self):
        """Stop the workflow execution."""
        self.stop_flag = True
        
    def _execute_action(self, action: Action) -> Optional[str]:
        """Execute a single action.
        
        Args:
            action: The Action to execute
            
        Returns:
            The ID of the next action to execute, or None if no next action
        """
        if not action.enabled:
            return action.next_action_id
            
        if action.type == ActionType.FIND_IMAGE:
            # Implement image recognition logic
            image_id = action.parameters.get("image_id")
            if not image_id or image_id not in self.project.images:
                raise ValueError(f"Invalid image ID: {image_id}")
                
            # TODO: Implement actual image recognition
            found = True  # Placeholder
            
            if action.type == ActionType.CONDITIONAL:
                return action.condition_true_id if found else action.condition_false_id
                
        elif action.type == ActionType.CLICK:
            # Implement mouse click logic
            import pyautogui
            x = action.parameters.get("x", 0)
            y = action.parameters.get("y", 0)
            button = action.parameters.get("button", "left")
            pyautogui.click(x=x, y=y, button=button)
            
        elif action.type == ActionType.MOVE_MOUSE:
            # Implement mouse movement logic
            import pyautogui
            x = action.parameters.get("x", 0)
            y = action.parameters.get("y", 0)
            duration = action.parameters.get("duration", 0.2)
            pyautogui.moveTo(x=x, y=y, duration=duration)
            
        elif action.type == ActionType.WAIT:
            # Implement wait logic
            duration = action.parameters.get("duration", 1.0)
            time.sleep(duration)
            
        elif action.type == ActionType.KEYBOARD_INPUT:
            # Implement keyboard input logic
            import pyautogui
            text = action.parameters.get("text", "")
            interval = action.parameters.get("interval", 0.1)
            pyautogui.write(text, interval=interval)
            
        elif action.type == ActionType.LOOP:
            # Implement loop logic
            iterations = action.parameters.get("iterations", 1)
            current_iteration = action.parameters.get("current_iteration", 0)
            
            if current_iteration < iterations:
                action.parameters["current_iteration"] = current_iteration + 1
                return action.condition_true_id
            else:
                action.parameters["current_iteration"] = 0
                return action.condition_false_id
                
        return action.next_action_id


class Workflow(QObject):
    """Represents an automation workflow."""
    
    def __init__(self, name="New Workflow"):
        super().__init__()
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = ""
        self.actions: Dict[str, Action] = {}
        self.start_action_id: Optional[str] = None
        self.is_running = False
        self.executor: Optional[WorkflowExecutor] = None
        
    def add_action(self, action: Action) -> str:
        """Add an action to the workflow.
        
        Args:
            action: The Action to add
            
        Returns:
            The ID of the added action
        """
        self.actions[action.id] = action
        
        # If this is the first action, set it as the start action
        if not self.start_action_id:
            self.start_action_id = action.id
            
        return action.id
        
    def remove_action(self, action_id: str) -> bool:
        """Remove an action from the workflow.
        
        Args:
            action_id: The ID of the action to remove
            
        Returns:
            True if the action was removed, False otherwise
        """
        if action_id in self.actions:
            # Update any actions that reference this one
            for action in self.actions.values():
                if action.next_action_id == action_id:
                    action.next_action_id = None
                if action.condition_true_id == action_id:
                    action.condition_true_id = None
                if action.condition_false_id == action_id:
                    action.condition_false_id = None
                    
            # If this was the start action, clear it
            if self.start_action_id == action_id:
                self.start_action_id = None
                
            del self.actions[action_id]
            return True
            
        return False
        
    def get_action(self, action_id: str) -> Optional[Action]:
        """Get an action by ID.
        
        Args:
            action_id: The ID of the action to get
            
        Returns:
            The Action object, or None if not found
        """
        return self.actions.get(action_id)
        
    def get_start_action(self) -> Optional[Action]:
        """Get the starting action of the workflow.
        
        Returns:
            The starting Action object, or None if no actions exist
        """
        if self.start_action_id:
            return self.actions.get(self.start_action_id)
        return None
        
    def connect_actions(self, from_id: str, to_id: str, condition: Optional[bool] = None):
        """Connect two actions in the workflow.
        
        Args:
            from_id: The ID of the source action
            to_id: The ID of the target action
            condition: For conditional actions, True for true branch, False for false branch
        """
        if from_id not in self.actions or to_id not in self.actions:
            raise ValueError("Invalid action IDs")
            
        from_action = self.actions[from_id]
        
        if from_action.type == ActionType.CONDITIONAL:
            if condition is None:
                raise ValueError("Condition required for conditional action")
            if condition:
                from_action.condition_true_id = to_id
            else:
                from_action.condition_false_id = to_id
        else:
            from_action.next_action_id = to_id
            
    def execute(self, project) -> bool:
        """Execute the workflow.
        
        Args:
            project: The Project object this workflow belongs to
            
        Returns:
            True if the workflow started successfully
        """
        if self.is_running:
            logger.warning("Workflow is already running")
            return False
            
        if not self.start_action_id:
            logger.error("No actions in workflow")
            return False
            
        self.executor = WorkflowExecutor(self, project)
        self.executor.workflow_completed.connect(self._on_workflow_completed)
        self.executor.workflow_stopped.connect(self._on_workflow_stopped)
        
        self.is_running = True
        self.executor.start()
        
        return True
        
    def stop(self):
        """Stop the workflow execution."""
        if self.is_running and self.executor:
            self.executor.stop()
            
    def _on_workflow_completed(self):
        """Handle workflow completion."""
        self.is_running = False
        self.executor = None
        logger.info(f"Workflow completed: {self.name}")
        
    def _on_workflow_stopped(self):
        """Handle workflow being stopped."""
        self.is_running = False
        self.executor = None
        logger.info(f"Workflow stopped: {self.name}")
