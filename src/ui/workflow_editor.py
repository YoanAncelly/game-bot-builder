#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Workflow Editor for Game Bot Builder

Provides a visual designer to create and configure bot workflows.
"""

import logging
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF

logger = logging.getLogger("GameBotBuilder")


class WorkflowEditor(QWidget):
    """Workflow Editor widget that provides a canvas to visually construct workflows."""
    status_message = Signal(str)
    
    def __init__(self, project):
        super().__init__()
        self.project = project
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWindowTitle("Workflow Editor")
        self.layout = QVBoxLayout(self)
        
        # Create a QGraphicsScene and QGraphicsView for the workflow canvas
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHints(self.view.renderHints())
        self.layout.addWidget(self.view)
        
        # Add a refresh button to update the workflow view
        self.refresh_button = QPushButton("Refresh Workflow", self)
        self.refresh_button.clicked.connect(self.refresh_scene)
        self.layout.addWidget(self.refresh_button)
        
        self.status_message.emit("Workflow Editor loaded")
        logger.info("Workflow Editor initialized")

    def refresh_scene(self):
        """Refresh the visual representation of the workflow."""
        self.scene.clear()
        workflow = self.project.workflows[0] if self.project.workflows else None
        if not workflow or not workflow.actions:
            self.scene.addText("No actions in workflow")
            self.status_message.emit("No actions in workflow")
            logger.error("No actions in workflow")
            return
        
        # Layout actions horizontally in order of execution
        node_items = {}
        x = 50
        y = 100
        spacing_x = 200  # More space between nodes
        rect_width = 150
        rect_height = 80
        
        # Create a node for each action in order
        ordered_actions = []
        current_action = workflow.get_start_action()
        
        # Follow the chain of next_action_id
        while current_action:
            ordered_actions.append(current_action)
            if current_action.next_action_id:
                current_action = workflow.get_action(current_action.next_action_id)
            else:
                current_action = None
        
        # Create nodes for each action
        for action in ordered_actions:
            # Create a colored rectangle based on action type
            color = self._get_color_for_action_type(action.type)
            rect_item = self.scene.addRect(x, y, rect_width, rect_height, 
                                          QPen(Qt.black, 2), 
                                          QBrush(color))
            
            # Add the action name
            text_item = self.scene.addText(action.name)
            text_item.setPos(x + (rect_width - text_item.boundingRect().width())/2, 
                             y + 10)
            
            # Add the action type below the name
            type_text = self.scene.addText(f"({action.type.value})")
            type_text.setPos(x + (rect_width - type_text.boundingRect().width())/2, 
                             y + 40)
            
            node_items[action.id] = (rect_item, x, y, rect_width, rect_height)
            x += spacing_x
        
        # Draw connections with arrows
        for action in ordered_actions:
            if action.next_action_id and action.next_action_id in node_items:
                _, x1, y1, w1, h1 = node_items[action.id]
                _, x2, y2, w2, h2 = node_items[action.next_action_id]
                
                # Draw line from right side of first node to left side of second node
                start_x = x1 + w1
                start_y = y1 + h1/2
                end_x = x2
                end_y = y2 + h2/2
                
                # Draw the connection line
                line_pen = QPen(Qt.black, 2)
                self.scene.addLine(start_x, start_y, end_x, end_y, line_pen)
                
                # Add an arrow at the end
                self._add_arrow(start_x, start_y, end_x, end_y)
        
        # Adjust the scene rect to fit all items
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.status_message.emit("Workflow Editor refreshed")
    
    def _add_arrow(self, start_x, start_y, end_x, end_y):
        """Add an arrow pointing to the end coordinates."""
        # Calculate the angle of the line
        dx = end_x - start_x
        dy = end_y - start_y
        angle = math.atan2(dy, dx)
        
        # Arrow dimensions
        arrow_size = 15
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrow points
        p1 = QPointF(end_x, end_y)
        p2 = QPointF(end_x - arrow_size * math.cos(angle - arrow_angle),
                     end_y - arrow_size * math.sin(angle - arrow_angle))
        p3 = QPointF(end_x - arrow_size * math.cos(angle + arrow_angle),
                     end_y - arrow_size * math.sin(angle + arrow_angle))
        
        # Create arrow polygon
        arrow = QPolygonF([p1, p2, p3])
        self.scene.addPolygon(arrow, QPen(Qt.black, 2), QBrush(Qt.black))
    
    def _get_color_for_action_type(self, action_type):
        """Return a color based on the action type."""
        colors = {
            "find_image": QColor(173, 216, 230),  # Light blue
            "click": QColor(144, 238, 144),      # Light green
            "move_mouse": QColor(255, 182, 193), # Light pink
            "wait": QColor(211, 211, 211),       # Light gray
            "keyboard_input": QColor(255, 222, 173), # Light orange
            "conditional": QColor(230, 230, 250), # Lavender
            "loop": QColor(255, 255, 224)         # Light yellow
        }
        return colors.get(action_type.value, QColor(240, 240, 240))

    def set_project(self, project):
        self.project = project
        self.refresh_scene()

    def _refresh(self):
        # Refresh method simply calls refresh_scene
        self.refresh_scene()
