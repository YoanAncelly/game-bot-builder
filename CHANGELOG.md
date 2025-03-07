# Game Bot Builder - Changelog

## Recent Implementations

### Image Recognition Panel UI Improvements (2025-03-07)

Redesigned the Image Recognition Panel UI to reduce clutter and improve usability:

- Reorganized UI components into logical, collapsible sections:
  - Image Selection at the top with a compact preview
  - Target Analysis in a distinct section with improved display
  - Basic Settings for common options
  - Advanced settings in collapsible groups (Color Filtering, Shape Matching, Multi-Scale Matching)
  - Results section at the bottom

- Added a scrollable interface that adapts to window size
- Improved Target Analysis display with better text rendering and formatting
  - Fixed text visibility with proper color contrast
  - Enhanced layout with proper spacing and margins
  - Used rich text formatting for better readability
- Implemented proper spacing and margins for improved readability
- Made controls more compact and aligned consistently
- Improved visual hierarchy with better grouping of related controls
- Added visual feedback with alternating row colors in results list
- Enhanced user documentation with detailed explanation of the Analyze Target feature and its benefits

These UI improvements make the image recognition panel significantly more intuitive and less cluttered, especially when using the advanced recognition features.

### Enhanced Image Recognition System (2025-03-07)

Implemented a significantly improved image recognition system to enhance target detection accuracy and reduce false positives:

- Added color filtering capability to the image recognition process:
  - Pre-filters screenshots to focus only on regions with colors similar to the target
  - Supports automatic color range detection based on target image analysis
  - Includes options for manual RGB range configuration for precise control
  - Implemented HSV color space conversion for more effective color-based filtering

- Added shape matching verification to reduce false positives:
  - Extracts contours from target images and potential matches
  - Compares shape characteristics to verify matches
  - Calculates shape metrics including circularity, area, perimeter
  - Automatically categorizes shapes (circle, square, rectangle, etc.)

- Implemented target image analysis feature:
  - Automatically extracts color and shape properties from target images
  - Provides visual feedback on target characteristics
  - Uses analysis to configure optimal detection settings

- Updated the image recognition panel with new UI elements:
  - Added target analysis section with analysis button and results display
  - Added color filtering controls with auto-detect option
  - Added shape matching controls with adjustable threshold
  - Organized settings into logical groups for better usability

- Improved the existing multi-scale matching:
  - Better integration with new filtering techniques
  - Optimized to prioritize best-matching scales

These enhancements significantly improve the bot's ability to accurately detect specific targets while minimizing false positives, particularly useful for applications like aim trainers where precise target identification is critical.

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