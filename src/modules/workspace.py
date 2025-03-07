#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Workspace module for Game Bot Builder

Handles screen capture and image recognition functionality.
"""

import os
import cv2
import numpy as np
import pyautogui
import logging
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QRect
from typing import Optional, Tuple, List

logger = logging.getLogger("GameBotBuilder")


class Workspace(QObject):
    """Manages screen capture and image recognition."""
    
    # Signals
    capture_taken = Signal(str)  # Path to captured image
    template_matched = Signal(QRect)  # Matched region
    
    def __init__(self):
        super().__init__()
        self.capture_directory = "captures"
        self.ensure_capture_directory()
        
    def ensure_capture_directory(self):
        """Ensure the capture directory exists."""
        if not os.path.exists(self.capture_directory):
            os.makedirs(self.capture_directory)
            logger.info(f"Created capture directory: {self.capture_directory}")
            
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Capture the screen or a region of it.
        
        Args:
            region: Optional tuple of (left, top, width, height) to capture
            
        Returns:
            Path to the saved screenshot
        """
        try:
            # Take the screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = os.path.join(self.capture_directory, filename)
            
            # Save the screenshot
            screenshot.save(filepath)
            logger.info(f"Screen captured: {filepath}")
            
            self.capture_taken.emit(filepath)
            return filepath
            
        except Exception as e:
            logger.error(f"Screen capture failed: {str(e)}")
            raise
            
    def find_template(self, template_path: str, screen_path: Optional[str] = None,
                     threshold: float = 0.8, use_multi_scale: bool = False,
                     scale_range: Tuple[float, float] = (0.8, 1.2),
                     scale_steps: int = 5, max_matches: int = 10,
                     use_color_filtering: bool = False,
                     color_range: Optional[Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = None,
                     match_shape: bool = False,
                     shape_threshold: float = 0.7) -> List[QRect]:
        """Find a template image within a screenshot.
        
        Args:
            template_path: Path to the template image to find
            screen_path: Optional path to the screenshot to search in. If None, takes a new screenshot
            threshold: Matching threshold (0-1), higher is more strict
            use_multi_scale: Whether to use multi-scale matching
            scale_range: Range of scales to try (min_scale, max_scale)
            scale_steps: Number of scale steps between min and max scale
            max_matches: Maximum number of matches to return
            use_color_filtering: Whether to filter by color before matching
            color_range: Optional tuple of (lower_bound, upper_bound) RGB values for color filtering
            match_shape: Whether to use shape matching as additional verification
            shape_threshold: Threshold for shape matching similarity (0-1)
            
        Returns:
            List of QRect objects representing matched regions
        """
        try:
            # Load the template
            template = cv2.imread(template_path)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
                
            # Get the screenshot
            if screen_path is None:
                screen_path = self.capture_screen()
                
            # Load the screenshot
            screenshot = cv2.imread(screen_path)
            if screenshot is None:
                raise ValueError(f"Failed to load screenshot: {screen_path}")
            
            # Apply color filtering if requested
            if use_color_filtering and color_range is not None:
                # Convert to HSV color space (better for color filtering)
                screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
                template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
                
                # Compute average color of template
                if color_range is None:
                    template_avg_color = np.mean(template_hsv, axis=(0, 1))
                    # Create a color range based on the average template color
                    color_tolerance = (20, 50, 50)  # H, S, V tolerances
                    lower_bound = np.array([max(0, template_avg_color[0] - color_tolerance[0]),
                                           max(0, template_avg_color[1] - color_tolerance[1]),
                                           max(0, template_avg_color[2] - color_tolerance[2])])
                    upper_bound = np.array([min(179, template_avg_color[0] + color_tolerance[0]),
                                           min(255, template_avg_color[1] + color_tolerance[1]),
                                           min(255, template_avg_color[2] + color_tolerance[2])])
                else:
                    # Convert RGB color range to HSV
                    lower_rgb, upper_rgb = color_range
                    lower_bound = np.array(cv2.cvtColor(np.uint8([[lower_rgb]]), cv2.COLOR_RGB2HSV)[0, 0])
                    upper_bound = np.array(cv2.cvtColor(np.uint8([[upper_rgb]]), cv2.COLOR_RGB2HSV)[0, 0])
                
                # Create mask based on color range
                color_mask = cv2.inRange(screenshot_hsv, lower_bound, upper_bound)
                
                # Apply mask to screenshot
                filtered_screenshot = cv2.bitwise_and(screenshot, screenshot, mask=color_mask)
                
                # For visualization and debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                mask_path = os.path.join(self.capture_directory, f"color_mask_{timestamp}.png")
                cv2.imwrite(mask_path, color_mask)
                filtered_path = os.path.join(self.capture_directory, f"filtered_{timestamp}.png")
                cv2.imwrite(filtered_path, filtered_screenshot)
                
                logger.info(f"Applied color filtering. Mask saved to: {mask_path}")
                
                # Use the filtered screenshot for further processing
                screenshot_for_matching = filtered_screenshot
            else:
                screenshot_for_matching = screenshot.copy()
                
            # Convert both images to grayscale
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            screenshot_gray = cv2.cvtColor(screenshot_for_matching, cv2.COLOR_BGR2GRAY)
            
            # Store original template for shape matching later
            original_template = template.copy()
            original_template_gray = template_gray.copy()
            
            matches = []
            
            if use_multi_scale:
                matches = self._multi_scale_template_matching(
                    screenshot_gray, template_gray, threshold, scale_range, scale_steps
                )
            else:
                # Perform regular template matching
                result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                
                # Get all matches above threshold
                locations = np.where(result >= threshold)
                
                template_h, template_w = template_gray.shape
                
                # Convert matches to QRect objects
                for pt in zip(*locations[::-1]):
                    rect = QRect(pt[0], pt[1], template_w, template_h)
                    matches.append(rect)
            
            # Apply shape matching if requested
            if match_shape and matches:
                # Extract template contours for shape matching
                template_contours = self._extract_contours(original_template_gray)
                
                if template_contours:
                    main_template_contour = max(template_contours, key=cv2.contourArea)
                    
                    # Filter matches based on shape similarity
                    filtered_matches = []
                    for rect in matches:
                        # Extract region from screenshot
                        region = screenshot_gray[rect.y():rect.y()+rect.height(), rect.x():rect.x()+rect.width()]
                        
                        # Check if region has valid dimensions
                        if region.shape[0] > 0 and region.shape[1] > 0:
                            # Extract contours from region
                            region_contours = self._extract_contours(region)
                            
                            if region_contours:
                                main_region_contour = max(region_contours, key=cv2.contourArea)
                                
                                # Compare shapes
                                shape_match = cv2.matchShapes(main_template_contour, main_region_contour, cv2.CONTOURS_MATCH_I2, 0.0)
                                logger.debug(f"Shape match score: {shape_match} (lower is better)")
                                
                                # Convert shape_match to similarity (1.0 = perfect match, 0.0 = no match)
                                # shape_match is 0 for perfect match, and increases for worse matches
                                similarity = max(0.0, 1.0 - shape_match)
                                
                                if similarity >= shape_threshold:
                                    filtered_matches.append(rect)
                                    logger.debug(f"Match passed shape verification with similarity {similarity:.2f}")
                                else:
                                    logger.debug(f"Match failed shape verification with similarity {similarity:.2f}")
                    
                    matches = filtered_matches
                    logger.info(f"After shape matching: {len(matches)} matches remain")
            
            # Apply non-maximum suppression to eliminate overlapping matches
            matches = self._apply_non_max_suppression(matches)
            
            # Limit the number of matches to avoid overwhelming the UI
            if len(matches) > max_matches:
                logger.warning(f"Found {len(matches)} matches, limiting to {max_matches}")
                matches = matches[:max_matches]
            
            # Emit signals for matches (after filtering)
            for rect in matches:
                self.template_matched.emit(rect)
                
            logger.info(f"Found {len(matches)} matches for template: {template_path}")
            return matches
            
        except Exception as e:
            logger.error(f"Template matching failed: {str(e)}")
            raise
    
    def _extract_contours(self, gray_image):
        """Extract contours from a grayscale image.
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of contours
        """
        # Apply threshold to get a binary image
        _, binary = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def analyze_target_image(self, template_path):
        """Analyze a target image to extract its color and shape characteristics.
        
        Args:
            template_path: Path to the template image to analyze
            
        Returns:
            Dictionary with color and shape information
        """
        try:
            # Load the template
            template = cv2.imread(template_path)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            # Convert to different color spaces
            template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Calculate average color
            avg_bgr = np.mean(template, axis=(0, 1))
            avg_hsv = np.mean(template_hsv, axis=(0, 1))
            
            # Extract color range
            std_hsv = np.std(template_hsv, axis=(0, 1))
            lower_hsv = np.array([max(0, avg_hsv[0] - 2*std_hsv[0]),
                               max(0, avg_hsv[1] - 2*std_hsv[1]),
                               max(0, avg_hsv[2] - 2*std_hsv[2])])
            upper_hsv = np.array([min(179, avg_hsv[0] + 2*std_hsv[0]),
                               min(255, avg_hsv[1] + 2*std_hsv[1]),
                               min(255, avg_hsv[2] + 2*std_hsv[2])])
            
            # Extract shape features
            contours = self._extract_contours(template_gray)
            shape_features = {}
            if contours:
                main_contour = max(contours, key=cv2.contourArea)
                # Calculate area, perimeter, circularity
                area = cv2.contourArea(main_contour)
                perimeter = cv2.arcLength(main_contour, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                # Approximate shape
                approx = cv2.approxPolyDP(main_contour, 0.04 * perimeter, True)
                
                # Determine shape type based on vertices count and circularity
                if circularity > 0.8:
                    shape_type = "circle"
                elif len(approx) == 3:
                    shape_type = "triangle"
                elif len(approx) == 4:
                    # Check if it's a square or rectangle
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / h
                    shape_type = "square" if 0.9 <= aspect_ratio <= 1.1 else "rectangle"
                else:
                    shape_type = "polygon"
                
                shape_features = {
                    "type": shape_type,
                    "vertices": len(approx),
                    "area": area,
                    "perimeter": perimeter,
                    "circularity": circularity
                }
            
            return {
                "avg_color_bgr": tuple(avg_bgr),
                "avg_color_hsv": tuple(avg_hsv),
                "color_range_hsv": (tuple(lower_hsv), tuple(upper_hsv)),
                "shape": shape_features
            }
            
        except Exception as e:
            logger.error(f"Target image analysis failed: {str(e)}")
            raise
            
    def _multi_scale_template_matching(self, screenshot_gray, template_gray, threshold, scale_range, scale_steps):
        """Perform template matching at multiple scales.
        
        Args:
            screenshot_gray: Grayscale screenshot image
            template_gray: Grayscale template image
            threshold: Matching threshold
            scale_range: Range of scales to try (min_scale, max_scale)
            scale_steps: Number of scale steps between min and max scale
            
        Returns:
            List of QRect objects representing matched regions
        """
        matches = []
        h, w = template_gray.shape
        screenshot_h, screenshot_w = screenshot_gray.shape
        
        # Calculate scales to try
        min_scale, max_scale = scale_range
        scale_increment = (max_scale - min_scale) / max(1, scale_steps - 1)
        scales = [min_scale + i * scale_increment for i in range(scale_steps)]
        
        best_confidence = 0
        best_scale = 1.0
        best_matches = []
        
        logger.info(f"Performing multi-scale matching with {len(scales)} scale levels")
        
        for scale in scales:
            # Skip scales that would make the template larger than the screenshot
            scaled_w = int(w * scale)
            scaled_h = int(h * scale)
            
            if scaled_w > screenshot_w or scaled_h > screenshot_h:
                logger.debug(f"Skipping scale {scale} - template too large")
                continue
            
            # Resize the template
            if scale != 1.0:
                scaled_template = cv2.resize(template_gray, (scaled_w, scaled_h))
            else:
                scaled_template = template_gray
                
            # Perform template matching
            try:
                result = cv2.matchTemplate(screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
                
                # Find the maximum matching value and its location
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Keep track of the best scale
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_scale = scale
                
                # Find all positions where the match quality exceeds the threshold
                # Use a slightly higher threshold for non-optimal scales to reduce false positives
                current_threshold = threshold
                if best_confidence > 0 and max_val < best_confidence * 0.9:
                    # If this scale's confidence is significantly lower than the best we've seen, 
                    # use a higher threshold to avoid false positives
                    current_threshold = threshold * 1.1
                
                locations = np.where(result >= current_threshold)
                
                # Get match locations
                scale_matches = []
                for pt in zip(*locations[::-1]):
                    rect = QRect(pt[0], pt[1], scaled_w, scaled_h)
                    scale_matches.append(rect)
                
                # Only keep the top matches from this scale
                if scale_matches:
                    # If this is the best scale we've seen so far, update best_matches
                    if max_val >= best_confidence * 0.95:  # Allow for some small difference
                        best_matches = scale_matches
                    
                    # Add to overall matches list
                    matches.extend(scale_matches[:5])  # Limit matches per scale
                    
                logger.debug(f"Scale {scale:.2f}: Found {len(scale_matches)} matches (confidence: {max_val:.3f})")
                
            except Exception as e:
                logger.warning(f"Template matching at scale {scale:.2f} failed: {str(e)}")
        
        # If we found a clearly superior scale, prioritize matches from that scale
        if best_matches and best_confidence >= threshold:
            logger.info(f"Best match found at scale {best_scale:.2f} with confidence {best_confidence:.3f}")
            # Prepend best scale matches so they'll be prioritized after non-max suppression
            matches = best_matches + [m for m in matches if m not in best_matches]
            
        # If no matches were found, log the best confidence we found
        if not matches and best_confidence < threshold:
            logger.info(f"No matches found above threshold. Best confidence: {best_confidence:.3f} at scale {best_scale:.2f}")
            
        return matches
            
    def _apply_non_max_suppression(self, matches: List[QRect], overlap_threshold: float = 0.3) -> List[QRect]:
        """Apply non-maximum suppression to filter out overlapping matches.
        
        Args:
            matches: List of QRect objects representing matches
            overlap_threshold: Maximum allowed overlap ratio (0-1)
            
        Returns:
            Filtered list of QRect objects
        """
        if not matches:
            return []
            
        # Convert QRects to a format easier to work with
        boxes = [(rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()) for rect in matches]
        
        # Calculate areas for each box
        areas = [(x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in boxes]
        
        # Sort by bottom-right y-coordinate
        indices = list(range(len(boxes)))
        indices.sort(key=lambda i: boxes[i][3], reverse=True)
        
        keep = []
        while indices:
            i = indices[0]
            keep.append(i)
            
            to_remove = [0]  # Always remove the current index
            x1_i, y1_i, x2_i, y2_i = boxes[i]
            area_i = areas[i]
            
            # Check each remaining box
            for j_idx, j in enumerate(indices[1:], 1):
                x1_j, y1_j, x2_j, y2_j = boxes[j]
                
                # Calculate intersection
                xx1 = max(x1_i, x1_j)
                yy1 = max(y1_i, y1_j)
                xx2 = min(x2_i, x2_j)
                yy2 = min(y2_i, y2_j)
                
                # Check if there is an intersection
                if xx2 > xx1 and yy2 > yy1:
                    intersection = (xx2 - xx1) * (yy2 - yy1)
                    overlap = intersection / min(area_i, areas[j])
                    
                    if overlap > overlap_threshold:
                        to_remove.append(j_idx)
            
            # Remove boxes marked for removal (in reverse order to maintain indices)
            for idx in sorted(to_remove, reverse=True):
                indices.pop(idx)
        
        # Return filtered matches
        return [matches[i] for i in keep]
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get the RGB color of a pixel at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (R, G, B) values
        """
        try:
            return pyautogui.pixel(x, y)
        except Exception as e:
            logger.error(f"Failed to get pixel color at ({x}, {y}): {str(e)}")
            raise
            
    def wait_for_image(self, template_path: str, timeout: float = 10.0,
                      interval: float = 0.5, use_multi_scale: bool = False,
                      scale_range: Tuple[float, float] = (0.8, 1.2),
                      scale_steps: int = 5) -> Optional[QRect]:
        """Wait for an image to appear on screen.
        
        Args:
            template_path: Path to the template image to wait for
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            use_multi_scale: Whether to use multi-scale matching
            scale_range: Range of scales to try (min_scale, max_scale)
            scale_steps: Number of scale steps between min and max scale
            
        Returns:
            QRect of the matched region if found, None if timeout
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                matches = self.find_template(
                    template_path, 
                    use_multi_scale=use_multi_scale,
                    scale_range=scale_range,
                    scale_steps=scale_steps
                )
                if matches:
                    return matches[0]
            except Exception as e:
                logger.warning(f"Error during image wait: {str(e)}")
                
            time.sleep(interval)
            
        logger.warning(f"Timeout waiting for image: {template_path}")
        return None
        
    def highlight_region(self, rect: QRect):
        """Highlight a region on screen for debugging purposes.
        
        Args:
            rect: QRect defining the region to highlight
        """
        try:
            import pyautogui
            
            # Save current mouse position
            old_pos = pyautogui.position()
            
            # Move mouse around the rectangle
            duration = 0.1  # Reduced from 0.2 to make highlighting faster
            pyautogui.moveTo(rect.left(), rect.top(), duration=duration)
            pyautogui.moveTo(rect.right(), rect.top(), duration=duration)
            pyautogui.moveTo(rect.right(), rect.bottom(), duration=duration)
            pyautogui.moveTo(rect.left(), rect.bottom(), duration=duration)
            pyautogui.moveTo(rect.left(), rect.top(), duration=duration)
            
            # Restore mouse position
            pyautogui.moveTo(old_pos.x, old_pos.y)
            
        except Exception as e:
            logger.error(f"Failed to highlight region: {str(e)}")
            
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen size.
        
        Returns:
            Tuple of (width, height)
        """
        return pyautogui.size()
