#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Actions Panel for Game Bot Builder

Provides UI controls for creating and configuring bot actions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QLineEdit,
    QComboBox, QListWidget, QListWidgetItem, QMessageBox,
    QFormLayout, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon

from src.modules.project import Project
from src.modules.workflow import Action, ActionType


class ActionConfigWidget(QWidget):
    """Widget for configuring action parameters."""
    
    def __init__(self, action_type: ActionType):
        super().__init__()
        self.action_type = action_type
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components based on action type."""
        layout = QFormLayout(self)
        
        if self.action_type == ActionType.FIND_IMAGE:
            # Image selection
            self.image_combo = QComboBox()
            layout.addRow("Target Image:", self.image_combo)
            
            # Threshold
            self.threshold = QDoubleSpinBox()
            self.threshold.setRange(0.0, 1.0)
            self.threshold.setSingleStep(0.05)
            self.threshold.setValue(0.8)
            layout.addRow("Match Threshold:", self.threshold)
            
        elif self.action_type == ActionType.CLICK:
            # Click type
            self.click_type = QComboBox()
            self.click_type.addItems(["left", "right", "middle", "double"])
            layout.addRow("Click Type:", self.click_type)
            
            # Coordinates
            self.x_coord = QSpinBox()
            self.x_coord.setRange(-9999, 9999)
            layout.addRow("X Coordinate:", self.x_coord)
            
            self.y_coord = QSpinBox()
            self.y_coord.setRange(-9999, 9999)
            layout.addRow("Y Coordinate:", self.y_coord)
            
        elif self.action_type == ActionType.MOVE_MOUSE:
            # Coordinates
            self.x_coord = QSpinBox()
            self.x_coord.setRange(-9999, 9999)
            layout.addRow("X Coordinate:", self.x_coord)
            
            self.y_coord = QSpinBox()
            self.y_coord.setRange(-9999, 9999)
            layout.addRow("Y Coordinate:", self.y_coord)
            
            # Movement duration
            self.duration = QDoubleSpinBox()
            self.duration.setRange(0.0, 10.0)
            self.duration.setSingleStep(0.1)
            self.duration.setValue(0.2)
            layout.addRow("Duration (seconds):", self.duration)
            
        elif self.action_type == ActionType.WAIT:
            # Wait duration
            self.duration = QDoubleSpinBox()
            self.duration.setRange(0.0, 3600.0)
            self.duration.setSingleStep(0.5)
            self.duration.setValue(1.0)
            layout.addRow("Duration (seconds):", self.duration)
            
        elif self.action_type == ActionType.KEYBOARD_INPUT:
            # Text input
            self.text_input = QLineEdit()
            layout.addRow("Text:", self.text_input)
            
            # Input interval
            self.interval = QDoubleSpinBox()
            self.interval.setRange(0.0, 1.0)
            self.interval.setSingleStep(0.05)
            self.interval.setValue(0.1)
            layout.addRow("Interval (seconds):", self.interval)
            
        elif self.action_type == ActionType.CONDITIONAL:
            # Condition type
            self.condition_type = QComboBox()
            self.condition_type.addItems(["Image Found", "Color Match", "Custom"])
            layout.addRow("Condition Type:", self.condition_type)
            
        elif self.action_type == ActionType.LOOP:
            # Number of iterations
            self.iterations = QSpinBox()
            self.iterations.setRange(1, 9999)
            self.iterations.setValue(1)
            layout.addRow("Iterations:", self.iterations)
            
    def get_parameters(self) -> dict:
        """Get the current parameter values.
        
        Returns:
            Dictionary of parameter values
        """
        params = {}
        
        if self.action_type == ActionType.FIND_IMAGE:
            params["image_id"] = self.image_combo.currentData()
            params["threshold"] = self.threshold.value()
            
        elif self.action_type == ActionType.CLICK:
            params["button"] = self.click_type.currentText()
            params["x"] = self.x_coord.value()
            params["y"] = self.y_coord.value()
            
        elif self.action_type == ActionType.MOVE_MOUSE:
            params["x"] = self.x_coord.value()
            params["y"] = self.y_coord.value()
            params["duration"] = self.duration.value()
            
        elif self.action_type == ActionType.WAIT:
            params["duration"] = self.duration.value()
            
        elif self.action_type == ActionType.KEYBOARD_INPUT:
            params["text"] = self.text_input.text()
            params["interval"] = self.interval.value()
            
        elif self.action_type == ActionType.CONDITIONAL:
            params["condition_type"] = self.condition_type.currentText()
            
        elif self.action_type == ActionType.LOOP:
            params["iterations"] = self.iterations.value()
            params["current_iteration"] = 0
            
        return params
        
    def set_parameters(self, params: dict):
        """Set parameter values.
        
        Args:
            params: Dictionary of parameter values
        """
        if self.action_type == ActionType.FIND_IMAGE:
            index = self.image_combo.findData(params.get("image_id"))
            if index >= 0:
                self.image_combo.setCurrentIndex(index)
            self.threshold.setValue(params.get("threshold", 0.8))
            
        elif self.action_type == ActionType.CLICK:
            index = self.click_type.findText(params.get("button", "left"))
            if index >= 0:
                self.click_type.setCurrentIndex(index)
            self.x_coord.setValue(params.get("x", 0))
            self.y_coord.setValue(params.get("y", 0))
            
        elif self.action_type == ActionType.MOVE_MOUSE:
            self.x_coord.setValue(params.get("x", 0))
            self.y_coord.setValue(params.get("y", 0))
            self.duration.setValue(params.get("duration", 0.2))
            
        elif self.action_type == ActionType.WAIT:
            self.duration.setValue(params.get("duration", 1.0))
            
        elif self.action_type == ActionType.KEYBOARD_INPUT:
            self.text_input.setText(params.get("text", ""))
            self.interval.setValue(params.get("interval", 0.1))
            
        elif self.action_type == ActionType.CONDITIONAL:
            index = self.condition_type.findText(params.get("condition_type", "Image Found"))
            if index >= 0:
                self.condition_type.setCurrentIndex(index)
                
        elif self.action_type == ActionType.LOOP:
            self.iterations.setValue(params.get("iterations", 1))
            
    def update_image_list(self, project: Project):
        """Update the image selection combo box.
        
        Args:
            project: The current Project instance
        """
        if self.action_type == ActionType.FIND_IMAGE:
            self.image_combo.clear()
            for image_id, image_data in project.images.items():
                self.image_combo.addItem(image_data["description"], image_id)


class ActionsPanel(QWidget):
    """Panel for creating and managing bot actions."""
    
    actions_updated = Signal()
    
    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Action Type Selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Action Type:"))
        self.action_type = QComboBox()
        for action_type in ActionType:
            self.action_type.addItem(action_type.value, action_type)
        self.action_type.currentIndexChanged.connect(self._on_action_type_changed)
        type_layout.addWidget(self.action_type)
        layout.addLayout(type_layout)
        
        # Action Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Action Name:"))
        self.action_name = QLineEdit()
        name_layout.addWidget(self.action_name)
        layout.addLayout(name_layout)
        
        # Action Configuration
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.config_stack = QStackedWidget()
        
        # Create config widgets for each action type
        self.config_widgets = {}
        for action_type in ActionType:
            widget = ActionConfigWidget(action_type)
            self.config_widgets[action_type] = widget
            self.config_stack.addWidget(widget)
            
        scroll_area.setWidget(self.config_stack)
        layout.addWidget(scroll_area)
        
        # Action List
        layout.addWidget(QLabel("Actions:"))
        self.actions_list = QListWidget()
        self.actions_list.itemSelectionChanged.connect(self._on_action_selected)
        layout.addWidget(self.actions_list)
        
        # Action Controls
        controls_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Action")
        self.add_btn.clicked.connect(self.add_action)
        controls_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("Update Action")
        self.update_btn.clicked.connect(self.update_action)
        controls_layout.addWidget(self.update_btn)
        
        self.remove_btn = QPushButton("Remove Action")
        self.remove_btn.clicked.connect(self.remove_action)
        controls_layout.addWidget(self.remove_btn)
        
        # Add Move Up and Move Down buttons
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_action_up)
        controls_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.move_action_down)
        controls_layout.addWidget(self.move_down_btn)
        
        layout.addLayout(controls_layout)
        
        # Connect project signals
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_actions_list)
        
        # Initial refresh
        self._refresh_actions_list()
        self._update_image_lists()
        
    def set_project(self, project: Project):
        """Set the current project.
        
        Args:
            project: The Project instance to use
        """
        if self.project:
            self.project.project_loaded.disconnect(self._on_project_loaded)
            self.project.project_modified.disconnect(self._refresh_actions_list)
            
        self.project = project
        
        self.project.project_loaded.connect(self._on_project_loaded)
        self.project.project_modified.connect(self._refresh_actions_list)
        
        self._refresh_actions_list()
        self._update_image_lists()
        
    @Slot()
    def add_action(self):
        """Add a new action to the workflow."""
        name = self.action_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter an action name")
            return
            
        # Get the selected action type
        action_type = self.action_type.currentData()
        
        # Get parameters from the config widget
        config_widget = self.config_widgets[action_type]
        parameters = config_widget.get_parameters()
        
        # Create the action
        action = Action(
            type=action_type,
            name=name,
            parameters=parameters
        )
        
        # Add to workflow and chain if necessary
        if self.project.workflows:
            workflow = self.project.workflows[0]  # Use first workflow for now
            if not workflow.start_action_id:
                # First action in the workflow
                workflow.add_action(action)
            else:
                # Find the last action in the chain
                last_action = workflow.get_start_action()
                while last_action.next_action_id:
                    next_act = workflow.get_action(last_action.next_action_id)
                    if not next_act:
                        break
                    last_action = next_act
                workflow.add_action(action)
                last_action.next_action_id = action.id
            self._refresh_actions_list()
            self.project.mark_modified()
            
            # Signal that actions have been updated
            self.actions_updated.emit()

    @Slot()
    def update_action(self):
        """Update the selected action."""
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action_id = current_item.data(Qt.UserRole)
        if not action_id:
            return
            
        # Get the workflow
        if not self.project.workflows:
            return
            
        workflow = self.project.workflows[0]  # Use first workflow for now
        action = workflow.get_action(action_id)
        if not action:
            return
            
        # Update action properties
        name = self.action_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter an action name")
            return
            
        action.name = name
        action.type = self.action_type.currentData()
        
        # Get parameters from the config widget
        config_widget = self.config_widgets[action.type]
        action.parameters = config_widget.get_parameters()
        
        self._refresh_actions_list()
        self.project.mark_modified()
        
        # Signal that actions have been updated
        self.actions_updated.emit()
        
    @Slot()
    def remove_action(self):
        """Remove the selected action."""
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action_id = current_item.data(Qt.UserRole)
        if not action_id:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this action?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.project.workflows:
                workflow = self.project.workflows[0]  # Use first workflow for now
                if workflow.remove_action(action_id):
                    self._refresh_actions_list()
                    self.project.mark_modified()
                    
                    # Signal that actions have been updated
                    self.actions_updated.emit()
                    
    def _refresh_actions_list(self):
        """Refresh the list of actions."""
        self.actions_list.clear()
        
        if not self.project.workflows:
            return
            
        workflow = self.project.workflows[0]  # Use first workflow for now
        
        # Get ordered list of actions based on workflow connections
        ordered_actions = self._get_ordered_actions(workflow)
        
        # Add actions to the list in execution order
        for action in ordered_actions:
            item = QListWidgetItem(f"{action.name} ({action.type.value})")
            item.setData(Qt.UserRole, action.id)
            self.actions_list.addItem(item)
            
    def _update_image_lists(self):
        """Update image lists in all config widgets."""
        for widget in self.config_widgets.values():
            widget.update_image_list(self.project)
            
    @Slot(int)
    def _on_action_type_changed(self, index: int):
        """Handle action type selection change.
        
        Args:
            index: New combo box index
        """
        action_type = self.action_type.currentData()
        self.config_stack.setCurrentWidget(self.config_widgets[action_type])
        
    @Slot()
    def _on_action_selected(self):
        """Handle action selection in the list."""
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action_id = current_item.data(Qt.UserRole)
        if not action_id:
            return
            
        # Get the workflow
        if not self.project.workflows:
            return
            
        workflow = self.project.workflows[0]  # Use first workflow for now
        action = workflow.get_action(action_id)
        if not action:
            return
            
        # Update UI with action properties
        self.action_name.setText(action.name)
        
        index = self.action_type.findData(action.type)
        if index >= 0:
            self.action_type.setCurrentIndex(index)
            
        # Update config widget
        config_widget = self.config_widgets[action.type]
        config_widget.set_parameters(action.parameters)
        
    @Slot(str)
    def _on_project_loaded(self, filename: str):
        """Handle project loaded event.
        
        Args:
            filename: Path to the loaded project file
        """
        self._refresh_actions_list()
        self._update_image_lists()

    @Slot()
    def move_action_up(self):
        """Move the selected action up in the workflow order."""
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action_id = current_item.data(Qt.UserRole)
        if not action_id:
            return
            
        # Get the workflow
        if not self.project.workflows:
            return
            
        workflow = self.project.workflows[0]  # Use first workflow for now
        
        # Get ordered list of actions
        ordered_actions = self._get_ordered_actions(workflow)
        if not ordered_actions or len(ordered_actions) < 2:
            return
            
        # Find the index of the current action
        current_index = -1
        for i, action in enumerate(ordered_actions):
            if action.id == action_id:
                current_index = i
                break
                
        if current_index <= 0:  # Can't move up if it's the first action
            return
            
        # Swap with the action above
        ordered_actions[current_index], ordered_actions[current_index-1] = \
            ordered_actions[current_index-1], ordered_actions[current_index]
            
        # Rebuild the workflow connections
        self._rebuild_workflow_connections(workflow, ordered_actions)
        
        # Refresh the UI
        self._refresh_actions_list()
        self.project.mark_modified()

        # Signal that actions have been updated
        self.actions_updated.emit()

        # Reselect the moved action
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            if item.data(Qt.UserRole) == action_id:
                self.actions_list.setCurrentItem(item)
                break
    
    @Slot()
    def move_action_down(self):
        """Move the selected action down in the workflow order."""
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action_id = current_item.data(Qt.UserRole)
        if not action_id:
            return
            
        # Get the workflow
        if not self.project.workflows:
            return
            
        workflow = self.project.workflows[0]  # Use first workflow for now
        
        # Get ordered list of actions
        ordered_actions = self._get_ordered_actions(workflow)
        if not ordered_actions or len(ordered_actions) < 2:
            return
            
        # Find the index of the current action
        current_index = -1
        for i, action in enumerate(ordered_actions):
            if action.id == action_id:
                current_index = i
                break
                
        if current_index < 0 or current_index >= len(ordered_actions) - 1:  # Can't move down if it's the last action
            return
            
        # Swap with the action below
        ordered_actions[current_index], ordered_actions[current_index+1] = \
            ordered_actions[current_index+1], ordered_actions[current_index]
            
        # Rebuild the workflow connections
        self._rebuild_workflow_connections(workflow, ordered_actions)
        
        # Refresh the UI
        self._refresh_actions_list()
        self.project.mark_modified()
        
        # Signal that actions have been updated
        self.actions_updated.emit()
        
        # Reselect the moved action
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            if item.data(Qt.UserRole) == action_id:
                self.actions_list.setCurrentItem(item)
                break
    
    def _get_ordered_actions(self, workflow):
        """Get an ordered list of actions based on their connections.
        
        Args:
            workflow: The Workflow object
            
        Returns:
            List of Action objects in execution order
        """
        if not workflow.start_action_id or not workflow.actions:
            return []
            
        ordered_actions = []
        current_action = workflow.get_start_action()
        
        # Follow the chain of next_action_id
        while current_action:
            ordered_actions.append(current_action)
            if current_action.next_action_id:
                current_action = workflow.get_action(current_action.next_action_id)
            else:
                current_action = None
                
        return ordered_actions
    
    def _rebuild_workflow_connections(self, workflow, ordered_actions):
        """Rebuild the workflow connections based on the ordered list of actions.
        
        Args:
            workflow: The Workflow object
            ordered_actions: List of Action objects in the desired order
        """
        if not ordered_actions:
            workflow.start_action_id = None
            return
            
        # Set the start action
        workflow.start_action_id = ordered_actions[0].id
        
        # Connect actions in sequence
        for i in range(len(ordered_actions) - 1):
            ordered_actions[i].next_action_id = ordered_actions[i+1].id
            
        # Clear the last action's next_action_id
        if ordered_actions:
            ordered_actions[-1].next_action_id = None
