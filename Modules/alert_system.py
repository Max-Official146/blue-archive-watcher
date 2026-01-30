"""
Alert System Module
Handles sound and notification alerts
"""

import winsound
import os
import time
from plyer import notification

class AlertSystem:
    """Manages alerts (sound + notifications)"""
    
    def __init__(self):
        self.last_alert_time = 0
        self.cooldown = 5  # seconds
        self.sound_file = None
        self.use_sound = True
        self.use_notification = True
    
    def play_sound(self):
        """Play alert sound"""
        if not self.use_sound:
            return
        
        try:
            if self.sound_file and os.path.exists(self.sound_file):
                # Play custom WAV file
                winsound.PlaySound(self.sound_file, 
                                 winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # Play default Windows notification beep
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            print(f"Sound error: {e}")
    
    def send_notification(self, title, message):
        """Send desktop notification"""
        if not self.use_notification:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Dialog Detector",
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def alert(self, message, details=None):
        """
        Trigger alert if cooldown has passed.
        
        Args:
            message (str): Alert message
            details (dict): Optional details to include
        
        Returns:
            bool: True if alert was sent, False if on cooldown
        """
        current_time = time.time()
        
        if current_time - self.last_alert_time > self.cooldown:
            # Play sound
            self.play_sound()
            
            # Format message with details
            full_message = message
            if details and 'confidence' in details:
                full_message += f"\nConfidence: {details['confidence']:.1%}"
            
            # Send notification
            self.send_notification("Dialog Detected!", full_message)
            
            self.last_alert_time = current_time
            return True
        
        return False