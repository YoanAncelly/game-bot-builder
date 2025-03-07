# Game Bot Builder - Changelog

## Recent Implementations

### Fix for Empty Target Image List in find_image Action Panel (2025-03-07)

Fixed the issue where the Target Image dropdown in the find_image action panel was empty or only showing the first image:

- Enhanced the `update_image_list` method in the `ActionConfigWidget` class to properly handle image data
- Added validation to ensure the project and image data exist before attempting to populate the dropdown
- Added type checking to ensure image data is properly structured
- Implemented functionality to preserve the currently selected image when refreshing the list
- Added error handling to make the image loading process more robust
- Connected the project's `project_modified` signal to a new `_on_project_modified` method in `ActionsPanel` to ensure image lists are updated whenever the project changes

This fix ensures that all captured images are properly displayed in the Target Image dropdown when configuring find_image actions, improving the user experience when creating image recognition-based workflows.

### Auto-reorder Actions in Left Panel Feature (2025-03-07)

Implemented automatic reordering of actions in the left panel when actions are moved up or down:

- Modified the `_refresh_actions_list` method in the `ActionsPanel` class to display actions in the correct execution order
- Used the existing `_get_ordered_actions` method to retrieve actions in their workflow execution order
- This ensures that the actions list in the left panel always reflects the actual workflow order after reordering actions

This implementation provides better visual consistency between the actions list and the workflow graph, making it easier for users to understand the execution flow of their automation workflows.

### Auto-refresh Workflow Feature (2025-03-07)

Implemented real-time workflow visualization updates when actions are modified:

- Added an `actions_updated` signal to the `ActionsPanel` class that gets emitted whenever actions are modified, including:

  - When a new action is added
  - When an existing action is updated
  - When an action is removed
  - When actions are reordered (moved up or down)

- Updated the `WorkflowEditor` class to connect to this signal and automatically refresh the workflow visualization

- Connected the `actions_updated` signal from the `ActionsPanel` to the `WorkflowEditor`'s `refresh_scene` method in the `MainWindow._connect_signals` method to ensure proper signal propagation

This implementation eliminates the need for manual refresh after action changes, providing a more seamless user experience while maintaining the "Refresh Workflow" button as a fallback option.