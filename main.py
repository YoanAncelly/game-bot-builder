#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game Bot Builder - Main Entry Point

A visual tool for creating game bots without coding.
Design automation workflows by capturing screen elements and defining actions.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.modules.logger import setup_logger
from src.modules.panic import start_panic_listener


def main():
    """Main entry point for the application."""
    # Set up logging
    logger = setup_logger()
    logger.info("Starting Game Bot Builder")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Game Bot Builder")
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    
    # Start the panic listener (press F12 to stop all workflows)
    panic_listener = start_panic_listener(window.project)
    
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
