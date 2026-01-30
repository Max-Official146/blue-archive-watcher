"""
Window Capturer Module
Captures screenshots of windows by title (even if minimized)
"""

import win32gui
import win32ui
import win32con
from PIL import Image
import numpy as np
import cv2

class WindowCapturer:
    """Captures screenshots of windows"""
    
    @staticmethod
    def capture(window_title):
        """
        Capture a screenshot of a window by its title.
        
        Args:
            window_title (str): Exact window title (case-sensitive)
        
        Returns:
            numpy.ndarray: BGR image or None if failed
        """
        try:
            # Find the window
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                return None
            
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Create device contexts
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Capture the window (3 = PW_RENDERFULLCONTENT)
            result = win32gui.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            
            if result == 1:
                # Get bitmap data
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                # Convert to PIL Image
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr,
                    'raw',
                    'BGRX',
                    0,
                    1
                )
                
                # Convert to numpy array (OpenCV format)
                img_np = np.array(img)
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            else:
                img_np = None
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return img_np
            
        except Exception as e:
            print(f"Capture error: {e}")
            return None
    
    @staticmethod
    def window_exists(window_title):
        """
        Check if a window with the given title exists.
        
        Args:
            window_title (str): Window title to check
        
        Returns:
            bool: True if window exists, False otherwise
        """
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            return hwnd != 0
        except:
            return False