# Game Bot Builder - Developer Documentation

## Project Overview

Game Bot Builder is a visual tool for creating game automation bots without coding. It allows users to design automation workflows by capturing screen elements and defining actions to be performed on those elements. The application is built using Python with PySide6 (Qt) for the user interface.

## Architecture

The project follows a modular architecture with clear separation between the core functionality and the user interface:

### Core Modules

- **Project**: Central data structure that manages all components of a bot project (workflows, images, settings)
- **Workflow**: Defines a sequence of actions that form an automation workflow
- **Workspace**: Handles screen capture and image recognition functionality
- **Logger**: Provides logging capabilities throughout the application
- **Panic**: Implements emergency stop functionality (F12 key) to halt all running workflows

### UI Components

- **MainWindow**: The primary application window that hosts all panels and controls
- **WorkspacePanel**: Interface for screen capture and workspace management
- **ImageRecognitionPanel**: Tools for image recognition and template matching
- **ActionsPanel**: Interface for creating and configuring automation actions
- **WorkflowEditor**: Visual editor for creating and connecting workflow actions

## Key Concepts

### Project

A Project is the top-level container for all bot-related data. It includes:

- Metadata (name, description, creation/modification dates)
- Collection of Workflows
- Image repository
- Application settings
- Serialization/deserialization logic for saving/loading projects

### Workflow

A Workflow is a sequence of Actions that define the bot's behavior. Key components include:

- Collection of Actions with defined relationships
- Execution logic via WorkflowExecutor
- Support for conditional branching and loops

### Action

An Action represents a single step in a workflow. Types of actions include:

- FIND_IMAGE: Locate a specific image on screen
- CLICK: Perform mouse clicks
- MOVE_MOUSE: Move the mouse cursor
- WAIT: Pause execution for a specified duration
- KEYBOARD_INPUT: Simulate keyboard input
- CONDITIONAL: Branch based on conditions
- LOOP: Repeat a sequence of actions

### Workspace

The Workspace handles screen interaction, including:

- Screen capture functionality
- Image recognition and template matching
- Multi-scale template matching for better recognition
- Non-maximum suppression to filter overlapping matches

## File Format

Projects are saved in a custom `.gbb` file format, which is essentially a JSON file containing:

- Project metadata
- Serialized workspace configuration
- Serialized workflows and actions
- References to image assets
- Application settings

## Development Workflow

### Adding New Action Types

1. Add the new action type to the `ActionType` enum in `workflow.py`
2. Implement the execution logic in the `_execute_action` method of `WorkflowExecutor`
3. Add UI components for configuring the action in `actions_panel.py`
4. Update the workflow editor to support the new action type

### Enhancing Image Recognition

1. Modify the `find_template` method in `workspace.py`
   - Added color filtering capabilities to filter out regions that don't match the target's color profile
   - Added shape matching to verify that detected regions match the target's shape characteristics
   - Combined with multi-scale matching for more robust detection
2. Added `analyze_target_image` method to automatically extract color and shape features from target images
3. Update the UI in `image_recognition_panel.py` to expose new functionality:
   - Added target analysis panel to examine target image properties
   - Added color filtering controls with auto-detection capability
   - Added shape matching controls to filter detected regions by shape similarity

The improved image recognition system uses a multi-step approach:
1. **Color filtering**: Filter the screenshot to focus only on regions with colors similar to the target
2. **Template matching**: Apply standard template matching algorithms to find potential matches
3. **Shape verification**: Verify matches by comparing their shape characteristics to the target
4. **Non-maximum suppression**: Filter out overlapping matches to prevent duplicates

This combination of techniques significantly improves detection accuracy while reducing false positives.

### Enhanced UI Layout

1. Improved the `ImageRecognitionPanel` UI with a cleaner layout:
   - Organized controls into logical sections (basic settings vs. advanced features)
   - Implemented collapsible sections for advanced features to reduce clutter
   - Added scrollable content area to accommodate all settings without overwhelming the user
   - Improved visual hierarchy and styling for better readability
   - Enhanced user feedback with better status indicators and result displays

2. UI organization principles:
   - Essential controls are always visible (image selection, basic settings)
   - Advanced features are hidden by default but easily accessible
   - Related controls are grouped together (color filtering, shape matching, multi-scale matching)
   - Consistent spacing, alignment, and sizing for better visual appeal

This improved layout makes the application more approachable for new users while still providing access to all advanced features when needed.

### Adding New UI Features

1. Create new panel classes in the `src/ui` directory
2. Update `main_window.py` to incorporate the new panels
3. Connect signals and slots to handle user interactions

## Dependencies

The project requires Python 3.11 and relies on the following key libraries:

- **PySide6**: Qt bindings for Python, used for the UI
- **OpenCV (cv2)**: Computer vision library for image recognition
- **PyAutoGUI**: Cross-platform GUI automation library
- **NumPy**: Numerical computing library used for image processing
- **jsonpickle**: JSON serialization library for Python objects

## Project Structure

```
/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # User-facing documentation
├── DEVBOOK.md             # Developer documentation
├── LICENSE.md             # License information
├── captures/              # Directory for screen captures
├── docs/                  # Documentation files
├── logs/                  # Log files
└── src/                   # Source code
    ├── modules/           # Core functionality
    │   ├── logger.py      # Logging setup
    │   ├── panic.py       # Emergency stop functionality
    │   ├── project.py     # Project management
    │   ├── workflow.py    # Workflow definition and execution
    │   └── workspace.py   # Screen capture and image recognition
    ├── resources/         # Application resources
    └── ui/                # User interface components
        ├── actions_panel.py           # UI for action configuration
        ├── image_recognition_panel.py  # UI for image recognition
        ├── main_window.py             # Main application window
        ├── workflow_editor.py         # Visual workflow editor
        └── workspace_panel.py         # UI for workspace management
```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use docstrings for all classes and methods
- Maintain type hints for function parameters and return values

### Error Handling

- Use appropriate exception handling to prevent crashes
- Log errors with sufficient context for debugging
- Provide user-friendly error messages in the UI

### Performance Considerations

- Image recognition operations can be CPU-intensive
- Run long operations in separate threads to keep the UI responsive
- Consider optimization techniques for template matching with large images

## Future Development

Potential areas for enhancement include:

- Advanced image recognition using machine learning
- More sophisticated action types (e.g., OCR, color detection)
- Plugin system for extending functionality
- Cloud integration for sharing and collaborating on bot projects
- Improved debugging and testing tools

## Troubleshooting

### Common Issues

- **Image Recognition Failures**: Adjust threshold parameters or try multi-scale matching
- **UI Responsiveness**: Ensure long-running operations are executed in separate threads
- **Serialization Errors**: Check for circular references in objects being serialized

### Debugging

- Check log files in the `logs/` directory
- Use the built-in logging system with appropriate log levels
- Consider adding more detailed logging for problematic areas
