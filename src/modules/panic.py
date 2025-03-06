#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Panic module for Game Bot Builder

Provides a global keyboard listener to stop all running workflows when a panic key is pressed.
"""

import logging
from pynput import keyboard

logger = logging.getLogger("GameBotBuilder")


def start_panic_listener(project):
    """
    Starts a global keyboard listener that listens for the F12 key.
    When F12 is pressed, calls project.stop_workflow() to stop all running workflows.
    
    Args:
        project: The current Project instance from which workflows can be stopped.
    
    Returns:
        The listener object (daemon thread).
    """

    def on_press(key):
        try:
            if key == keyboard.Key.f12:
                logger.info("Panic button activated (F12). Stopping all workflows.")
                project.stop_workflow()
        except Exception as e:
            logger.error(f"Error in panic listener: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener
