# Game Bot Builder

A visual tool for creating game bots without coding. Design automation workflows by capturing screen elements and defining actions.

## Features

- Image recognition to detect game elements
- Mouse movement and click automation
- Visual workflow builder
- Save and load automation scripts
- Real-time monitoring
- Step-by-step execution

## Installation

1. **Python Requirement**: This project requires Python 3.11. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3110/).

   **If you have multiple Python versions installed:**
   
   If you have Python 3.12 or another version already installed, you can use one of these approaches:
   
   - **Python Launcher (recommended):** Use `py -3.11` instead of `python` in all commands
   - **Full path:** Use the complete path to Python 3.11 (e.g., `C:\Python311\python.exe`)
   - **Temporary PATH adjustment:** Run `set PATH=C:\Python311;%PATH%` before other commands

2. Clone this repository.

3. Create a virtual environment:
   - Open a terminal (Command Prompt or PowerShell) and navigate to the project directory.
   - Run: `python -m venv venv`
   - Activate the virtual environment:
     - For Command Prompt: `venv\Scripts\activate`
     - For PowerShell: `./venv/Scripts/Activate.ps1`
     - If you encounter execution policy issues in PowerShell, run:
       `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

4. Install dependencies:
   - Run: `python -m pip install --upgrade pip setuptools wheel`
   - Then: `pip install -r requirements.txt`

5. Run the application with: `python main.py`

## Usage

See the [documentation](docs/USER_GUIDE.md) for detailed usage instructions.

## Development Status

This project is currently in active development. See [ROADMAP.md](docs/ROADMAP.md) for planned features and progress.
