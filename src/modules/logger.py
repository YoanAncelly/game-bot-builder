#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger module for Game Bot Builder
"""

import logging
import os
from datetime import datetime


def setup_logger(level=logging.INFO):
    """Set up and configure the application logger.
    
    Args:
        level: The logging level (default: INFO)
        
    Returns:
        A configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/gamebotbuilder_{timestamp}.log"
    
    # Configure logger
    logger = logging.getLogger("GameBotBuilder")
    logger.setLevel(level)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
