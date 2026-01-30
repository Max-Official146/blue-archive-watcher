"""
Monitor Module
Main monitoring logic that combines all components
"""

import time
import threading
import queue
from .window_capturer import WindowCapturer
from .dialog_detector import DialogDetector
from .alert_system import AlertSystem

class Monitor:
    """Monitors game window for dialog boxes"""
    
    def __init__(self, template_folder="templates"):
        self.running = False
        self.window_title = ""
        self.scan_interval = 2.0
        self.detection_threshold = 0.8
        self.result_queue = queue.Queue()
        
        # Initialize components
        self.detector = DialogDetector(template_folder)
        self.alert_system = AlertSystem()
        
        self.monitor_thread = None
    
    def monitor_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        print(f"🔍 Monitoring started: {self.window_title}")
        print(f"   Threshold: {self.detection_threshold:.0%}")
        print(f"   Interval: {self.scan_interval}s")
        
        while self.running:
            try:
                # Capture window
                screenshot = WindowCapturer.capture(self.window_title)
                
                if screenshot is not None:
                    # Detect dialog
                    detected, details, debug_img = self.detector.detect(
                        screenshot, 
                        self.detection_threshold
                    )
                    
                    # Send result to GUI
                    result = {
                        'detected': detected,
                        'image': debug_img,
                        'timestamp': time.strftime("%H:%M:%S"),
                        'details': details
                    }
                    
                    self.result_queue.put(result)
                    
                    # Alert if detected
                    if detected:
                        self.alert_system.alert(
                            f"Template: {details['template']}", 
                            details
                        )
                        print(f"[{result['timestamp']}] ✅ Dialog detected: "
                              f"{details['template']} ({details['confidence']:.1%})")
                
                else:
                    # Window not found
                    self.result_queue.put({
                        'detected': False,
                        'image': None,
                        'timestamp': time.strftime("%H:%M:%S"),
                        'error': 'Window not found'
                    })
                
                # Wait before next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                self.result_queue.put({
                    'detected': False,
                    'image': None,
                    'timestamp': time.strftime("%H:%M:%S"),
                    'error': str(e)
                })
                time.sleep(self.scan_interval)
        
        print("🛑 Monitoring stopped")
    
    def start(self):
        """Start monitoring in background thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(
                target=self.monitor_loop, 
                daemon=True
            )
            self.monitor_thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False