"""
Dialog Detector Module
Detects dialog boxes using template matching
"""

import cv2
import numpy as np
import os

class DialogDetector:
    """Detects dialogs using template matching"""
    
    def __init__(self, template_folder="templates"):
        """
        Initialize detector with template images.
        
        Args:
            template_folder (str): Folder containing template images
        """
        self.template_folder = template_folder
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all template images from the templates folder"""
        if not os.path.exists(self.template_folder):
            print(f"⚠️  Template folder '{self.template_folder}' not found")
            print(f"   Creating folder...")
            os.makedirs(self.template_folder)
            print(f"   Place your template images (PNG/JPG) in: {os.path.abspath(self.template_folder)}")
            return
        
        # Load all image files
        template_files = [f for f in os.listdir(self.template_folder) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not template_files:
            print(f"⚠️  No template images found in '{self.template_folder}'")
            print(f"   Add template images to: {os.path.abspath(self.template_folder)}")
            return
        
        # Load each template
        for filename in template_files:
            filepath = os.path.join(self.template_folder, filename)
            template = cv2.imread(filepath)
            
            if template is not None:
                template_name = os.path.splitext(filename)[0]
                self.templates[template_name] = template
                h, w = template.shape[:2]
                print(f"✅ Loaded template: {template_name} ({w}x{h})")
            else:
                print(f"❌ Failed to load: {filename}")
        
        if not self.templates:
            print(f"⚠️  No valid templates loaded!")
    
    def detect(self, screenshot, threshold=0.8):
        """
        Detect if any template matches in the screenshot.
        
        TEMPLATE MATCHING:
        - Slides template across screenshot
        - Calculates similarity at each position
        - Returns best match if above threshold
        
        Args:
            screenshot: BGR image from window capture
            threshold: Match threshold (0.0-1.0, higher = more strict)
                      0.8 = 80% similarity required
                      0.9 = 90% similarity required (more strict)
                      0.7 = 70% similarity required (less strict)
        
        Returns:
            tuple: (detected: bool, details: dict, debug_img: numpy.ndarray)
        """
        if screenshot is None:
            return False, {}, None
        
        if not self.templates:
            # No templates loaded, return False
            return False, {'error': 'No templates loaded'}, screenshot
        
        debug_img = screenshot.copy()
        best_match = None
        best_confidence = 0
        
        # Try matching each template
        for template_name, template in self.templates.items():
            # Get template dimensions
            h, w = template.shape[:2]
            
            # Skip if template is larger than screenshot
            if h > screenshot.shape[0] or w > screenshot.shape[1]:
                continue
            
            # Perform template matching
            # TM_CCOEFF_NORMED = normalized cross-correlation
            # Returns value -1.0 to 1.0 (we normalize to 0-1)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            # Find best match location
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # max_val is the confidence (0-1)
            confidence = max_val
            
            # Check if this is the best match so far
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = {
                    'template': template_name,
                    'confidence': confidence,
                    'location': max_loc,
                    'size': (w, h)
                }
        
        # Check if best match exceeds threshold
        if best_match and best_confidence >= threshold:
            # Draw rectangle around match
            x, y = best_match['location']
            w, h = best_match['size']
            
            # Green rectangle for match
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            # Add label with confidence
            label = f"{best_match['template']}: {best_confidence:.1%}"
            cv2.putText(debug_img, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return True, best_match, debug_img
        else:
            # No match found
            details = {
                'best_confidence': best_confidence,
                'threshold': threshold,
                'templates_checked': len(self.templates)
            }
            return False, details, debug_img
    
    def add_template(self, name, image):
        """
        Add a template programmatically.
        
        Args:
            name (str): Template name
            image: BGR image (numpy array)
        """
        self.templates[name] = image
        h, w = image.shape[:2]
        print(f"✅ Added template: {name} ({w}x{h})")
    
    def save_template_from_screenshot(self, screenshot, name, roi=None):
        """
        Save a region of a screenshot as a template.
        
        Args:
            screenshot: Full screenshot
            name (str): Template name to save as
            roi (tuple): Region of interest (x, y, w, h) or None for full image
        """
        if roi:
            x, y, w, h = roi
            template = screenshot[y:y+h, x:x+w]
        else:
            template = screenshot
        
        filepath = os.path.join(self.template_folder, f"{name}.png")
        cv2.imwrite(filepath, template)
        print(f"💾 Saved template: {filepath}")
        
        # Reload templates
        self.load_templates()