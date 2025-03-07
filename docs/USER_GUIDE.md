# Game Bot Builder User Guide

Welcome to the Game Bot Builder! This guide will help you get started with installing, configuring, and using our visual bot creation tool.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [User Interface Overview](#user-interface-overview)
   - [Main Window](#main-window)
   - [Workspace Panel](#workspace-panel)
   - [Image Recognition Panel](#image-recognition-panel)
   - [Actions Panel](#actions-panel)
   - [Workflow Editor](#workflow-editor)
5. [Creating and Managing Bots](#creating-and-managing-bots)
6. [Troubleshooting & FAQs](#troubleshooting--faqs)
7. [Future Enhancements](#future-enhancements)

---

## Overview

The Game Bot Builder is a visual tool designed to allow you to create, test, and manage game automation scripts without writing code. You can capture screen regions, perform image recognition, and configure actions (such as mouse clicks, movements, waits, and keyboard inputs) that form a workflow for your bot.

## Installation

**Important: Game Bot Builder requires Python 3.11.** Other versions may cause compatibility issues with the dependencies.

Follow these steps to install and set up the project on Windows using a virtual environment:

1. **Install Python 3.11**

   Download and install Python 3.11 from the [official Python website](https://www.python.org/downloads/release/python-3110/).
   
   During installation, ensure you check the option to "Add Python to PATH".
   
   **Note for users with multiple Python versions:**
   
   If you have Python 3.12 or another version already installed (check with `python --version`), you have several options:
   
   a) **Use Python Launcher (recommended):**
      - After installing Python 3.11, use the Python Launcher to specify version 3.11:
      - Create the virtual environment with: `py -3.11 -m venv venv`
      - For all other commands, replace `python` with `py -3.11`
   
   b) **Use the full path to Python 3.11:**
      - Find the installation path (typically `C:\Python311\python.exe`)
      - Use the full path for commands: `C:\Python311\python.exe -m venv venv`
   
   c) **Modify PATH temporarily:**
      - Open a new command prompt
      - Set PATH to prioritize Python 3.11: `set PATH=C:\Python311;%PATH%`
      - Verify with `python --version` that you're using 3.11
      - Then proceed with the normal installation steps

2. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd game-bot-builder
   ```

3. **Create and Activate a Virtual Environment**

   - Open a terminal (Command Prompt or PowerShell) in the project directory.
   - Create the virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Command Prompt:**
       ```bash
       venv\Scripts\activate
       ```
     - **PowerShell:**
       ```bash
       ./venv/Scripts/Activate.ps1
       ```
       _Tip: If you run into execution policy issues in PowerShell, run:_
       ```bash
       Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
       ```

4. **Upgrade Package Tools and Install Dependencies**
   Upgrade pip, setuptools, and wheel before installing dependencies:

   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

   Then, install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. **Run the Application**
   Launch the bot builder by running:
   ```bash
   python main.py
   ```

## Running the Application

When you run the application, a main window will open. This is the central hub from which you can:

- Create a new project or open an existing one.
- Capture screen snapshots or select specific regions for your bot to target.
- Test image recognition with your chosen images.
- Configure various actions (clicks, moves, waits, etc.) that define your bot's behavior.
- Visually create and manage your workflow (the sequence of actions that will be executed by your bot).

## User Interface Overview

### Main Window

The main window is divided into two primary areas:

- **Left Panels (Tabs):** Contains tools for managing your project:

  - **Workspace Panel:** Capture screenshots and manage images.
  - **Image Recognition Panel:** Set image matching parameters and perform recognition tests.
  - **Actions Panel:** Configure and add different types of actions.

- **Right Panel:**
  - **Workflow Editor:** A visual canvas where your bot's workflow is displayed. (This is a placeholder for future drag-and-drop functionality.)

### Workspace Panel

- **Capture Options:** Use "Capture Screen" for full screen or "Capture Region" to capture a specific area by specifying x, y, width, and height.
- **Image List:** Displays images captured or added to the project. Selecting an image shows a preview.

### Image Recognition Panel

- **Image Selection:** Choose from your list of captured images for recognition tests.
- **Target Analysis:** Analyze your target image to extract important features.
  - **Analyze Target:** Click this button to automatically extract color and shape information from the selected image.
  - **Analysis Results:** Shows the detected color and shape characteristics of the target image in a rich text display.
- **Basic Settings:** Adjust the most common recognition parameters.
  - **Match Threshold:** Control how strict the matching algorithm should be (higher values require more precise matches).
  - **Match Mode:** Select the algorithm used for template matching.
  - **Convert to Grayscale:** Process images in grayscale for faster matching.
  - **Highlight Matches:** Visually highlight matches in the result window.
- **Advanced Settings:** Collapsible sections for more specialized recognition features.
  - **Color Filtering:** Enable this feature to pre-filter the screenshot by color before template matching.
    - **Auto-detect Color Range:** Automatically determine the color range based on the target image.
    - **Custom Color Range:** Manually set RGB values for the lower and upper bounds of the color filter.
  - **Shape Matching:** Enable this feature to verify matches by comparing their shape to the target image.
    - **Shape Threshold:** Control how strictly shapes should match (higher values require more similar shapes).
  - **Multi-Scale Matching:** Enable this feature to detect images at different scales.
    - **Min Scale/Max Scale:** Define the range of scaling to search for (e.g., 0.8-1.2 means the template might be 80%-120% of its original size).
    - **Scale Steps:** Number of scale increments to check between min and max scales (more steps means finer granularity but slower performance).
- **Testing:** Use "Test Recognition" to take a new screenshot and see if the selected image appears on the screen.
- **Results:** Displays a list of matches found during testing, including their positions and confidence scores.

#### Advanced Image Recognition Features

The enhanced image recognition system combines multiple techniques to dramatically improve detection accuracy:

##### Target Analysis
Before using any image for detection, you can analyze it to understand its properties:
1. Select your target image in the list
2. Click "Analyze Target"
3. Review the color and shape information
4. This analysis helps automatically configure optimal settings for detection

##### Color Filtering
This feature filters the screenshot to focus only on regions with colors similar to your target:

- **When to use:** Enable color filtering when:
  - Your target has a distinctive color (like orange circles in aim trainers)
  - Background elements cause false positives
  - You need to distinguish between similar shapes with different colors
  
- **Auto vs. Manual:** 
  - Auto-detect works well for most targets with uniform colors
  - Use manual RGB range setting for more precise control or for targets with multiple colors

##### Shape Matching
After finding potential matches by template matching, this feature verifies them by shape:

- **When to use:** Enable shape matching when:
  - False positives have similar colors but different shapes (e.g., mistaking circles for squares)
  - You need to focus on the exact shape regardless of internal details
  - Template matching alone yields too many incorrect matches
  
- **How it works:** The system extracts contours from both the target and potential matches, then compares their shapes. Only matches with similar shapes are kept.

##### Multi-Scale Matching

This advanced feature helps solve recognition problems when the target image appears at different sizes in the game:

- **When to use:** Enable multi-scale matching when:
  - The game interface changes size (e.g., different resolution settings)
  - UI elements scale based on in-game factors
  - You're experiencing false negatives with standard matching
- **How it works:** The system automatically checks multiple rescaled versions of your template image against the screen, finding the best match.
- **Performance note:** Using multi-scale matching increases processing time, as the system must perform multiple template matching operations at different scales.

#### Recommended Settings for Common Scenarios

- **Fast-Paced Games (e.g., aim trainers):**
  - Enable color filtering with auto-detection
  - Enable shape matching with threshold around 0.7
  - Set match threshold to 0.75-0.85
  - Use multi-scale matching only if necessary

- **UI Elements in Strategy Games:**
  - Use higher match threshold (0.85-0.95)
  - Shape matching often unnecessary
  - Color filtering helpful for buttons and icons

- **Hard-to-Detect Moving Targets:**
  - Enable all three advanced features
  - Use lower match threshold (0.6-0.7)
  - Increase scale steps to 7-10
  - Use wider scale range (e.g., 0.7-1.3)

### Actions Panel

- **Action Creation:** Select an action type (e.g., click, move, wait, keyboard input) and fill in its parameters.
- **Action List:** Manage and edit actions that are part of your workflow.
- **Workflow Integration:** Actions added here will be placed into your current workflow.

### Workflow Editor

- **Visual Workflow:** Displays a graphical representation of your workflow. (Currently a placeholder design.)
- **Future Features:** Planned enhancements include drag-and-drop functionality and more intuitive workflow management.

## Creating and Managing Bots

1. **Start a New Project:** Use the File menu to create a new project or open an existing one.
2. **Capture and Add Images:** Use the Workspace Panel to capture your game screen or region, and add important images for later recognition tasks.
3. **Set Up Image Recognition:** In the Image Recognition Panel, adjust the settings, test the recognition, and confirm the target images are correctly detected.
4. **Define Actions:** In the Actions Panel, add actions like clicks, moves, waits, or keyboard inputs. Each action can be configured with precise parameters.
5. **Design the Workflow:** The Workflow Editor shows the sequence of actions. Arrange and modify the workflow as needed.
6. **Run and Monitor Your Bot:** Use the toolbar options (Run Bot/Stop Bot) to execute your workflow and monitor its progress.

## Troubleshooting & FAQs

- **Installation Issues:**

  - Ensure you're using a compatible Python version (Python 3.11 is recommended for smoother compatibility).
  - Double-check that your virtual environment is activated before installing dependencies or running the application.

- **Dependency Errors:**

  - If you encounter errors related to removed modules (e.g., `pkgutil.ImpImporter`), consider downgrading Python to 3.11 until all packages are updated for Python 3.12/3.13.

- **Image Recognition Problems:**

  - If standard recognition fails to detect your template, try enabling multi-scale matching and adjust the scale range.
  - For UI elements that may appear at different sizes, start with a scale range of 0.8-1.2 and 5 scale steps.
  - Increasing the number of scale steps improves accuracy but reduces performance.
  - Consider lowering the match threshold slightly (e.g., from 0.8 to 0.7) when using multi-scale matching.

- **Tool Usage:**
  - If you're unsure about how to use a specific panel, refer back to the corresponding section of this guide for an overview and step-by-step instructions.

## Future Enhancements

- Improved visual workflow editor with drag-and-drop capabilities.
- Extended action options and customization.
- Enhanced troubleshooting tools and logging information within the UI.

---

We hope this guide helps you understand and efficiently use the Game Bot Builder. For additional questions or feedback, please refer to the [README](../README.md) or contact support.
