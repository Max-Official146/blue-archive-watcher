import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import win32gui
import threading
import time
import os
from plyer import notification
import winsound
import mss

class DialogDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blue Archive Dialog Detector 🌸 (MSS Version)")
        self.root.geometry("600x800")
        
        # State variables
        self.running = False
        self.selected_window_hwnd = None
        self.template_img = None
        self.monitor_thread = None
        self.sct = mss.mss() # Initialize the screen capture tool
        self.scan_interval = 2.0
        self.confidence_threshold = 0.8
        
        # --- UI Layout ---
        
        # 1. Top Bar: Window Selection
        frame_top = ttk.LabelFrame(root, text="1. Select Game Window")
        frame_top.pack(fill="x", padx=10, pady=5)
        
        self.window_combo = ttk.Combobox(frame_top, state="readonly")
        self.window_combo.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.window_combo.bind("<<ComboboxSelected>>", self.on_window_select)
        
        btn_refresh = ttk.Button(frame_top, text="🔄 Refresh List", command=self.refresh_windows)
        btn_refresh.pack(side="right", padx=5)

        # 2. Preview Area (Canvas)
        self.preview_frame = ttk.LabelFrame(root, text="2. Confirmation Preview")
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(self.preview_frame, bg="#2b2b2b")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas_text = self.canvas.create_text(
            290, 150, 
            text="Select window above!\n(Window MUST be visible on screen)", 
            fill="white", justify="center"
        )

        # 3. Settings & Actions
        frame_controls = ttk.LabelFrame(root, text="3. Controls")
        frame_controls.pack(fill="x", padx=10, pady=5)
        
        # Template Creator
        btn_template = ttk.Button(frame_controls, text="✂️ Create Template", command=self.open_crop_tool)
        btn_template.pack(side="left", padx=5, pady=10)
        
        self.lbl_template_status = ttk.Label(frame_controls, text="No template loaded ❌", foreground="red")
        self.lbl_template_status.pack(side="left", padx=5)

        # Monitor Toggle
        self.btn_monitor = ttk.Button(frame_controls, text="▶️ Start Monitoring", command=self.toggle_monitoring, state="disabled")
        self.btn_monitor.pack(side="right", padx=5, pady=10)

        # 4. Logs
        frame_log = ttk.LabelFrame(root, text="Activity Log")
        frame_log.pack(fill="x", padx=10, pady=5)
        self.log_var = tk.StringVar(value="Ready! Select your Blue Archive window to start.")
        ttk.Label(frame_log, textvariable=self.log_var).pack(anchor="w", padx=5, pady=5)

        # Initial load
        self.refresh_windows()

    def log(self, msg):
        self.log_var.set(msg)
        self.root.update_idletasks()

    # --- Robust Window Capture (MSS) ---
    def get_windows_dict(self):
        windows = {}
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows[title] = hwnd
        win32gui.EnumWindows(callback, None)
        return windows

    def refresh_windows(self):
        self.windows_map = self.get_windows_dict()
        self.window_combo['values'] = list(self.windows_map.keys())
        self.log("Window list refreshed.")

    def capture_window_area(self, hwnd):
        """
        Finds the window coordinates and grabs that area from the screen using MSS.
        """
        try:
            # Get window coordinates
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            w, h = x2 - x, y2 - y
            
            if w <= 0 or h <= 0: return None

            # Clean up borders (Windows 11 adds invisible borders sometimes)
            # You might need to tweak these if the image includes too much 'desktop' background
            monitor = {"top": y, "left": x, "width": w, "height": h}
            
            # Capture
            sct_img = self.sct.grab(monitor)
            
            # Convert to OpenCV/Numpy format
            img = np.array(sct_img)
            # MSS returns BGRA, OpenCV needs BGR (drop alpha channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img

        except Exception as e:
            self.log(f"Capture failed: {e}")
            return None

    def on_window_select(self, event):
        title = self.window_combo.get()
        if title in self.windows_map:
            self.selected_window_hwnd = self.windows_map[title]
            
            # Attempt to bring window to front so we can see it
            try:
                win32gui.SetForegroundWindow(self.selected_window_hwnd)
                time.sleep(0.2) 
            except: pass

            frame = self.capture_window_area(self.selected_window_hwnd)
            
            if frame is not None:
                self.show_preview(frame)
                self.log(f"✅ Preview loaded for: {title}")
            else:
                self.log("❌ Capture failed.")

    def show_preview(self, cv_img):
        # Resize and display
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv_img)
        
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()
        if c_w < 10: c_w, c_h = 580, 400
        
        img_w, img_h = pil_img.size
        ratio = min(c_w/img_w, c_h/img_h)
        new_size = (int(img_w * ratio), int(img_h * ratio))
        
        pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(pil_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(c_w//2, c_h//2, image=self.tk_image, anchor="center")

    # --- Cropping / Template Tool ---
    def open_crop_tool(self):
        if not self.selected_window_hwnd:
            messagebox.showwarning("Wait", "Please select the game window first!")
            return

        frame = self.capture_window_area(self.selected_window_hwnd)
        if frame is None:
            messagebox.showerror("Error", "Could not capture game for cropping.")
            return

        cv2.imwrite("temp_crop.png", frame)
        
        # Create Cropper Window
        top = tk.Toplevel(self.root)
        top.title("Drag to Select Template Area")
        top.state('zoomed')

        raw_img = Image.open("temp_crop.png")
        tk_img = ImageTk.PhotoImage(raw_img)
        
        canvas = tk.Canvas(top, cursor="cross")
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=tk_img, anchor="nw")
        
        rect_data = {"start_x": 0, "start_y": 0, "rect_id": None}

        def on_mouse_down(event):
            rect_data["start_x"] = canvas.canvasx(event.x)
            rect_data["start_y"] = canvas.canvasy(event.y)

        def on_mouse_drag(event):
            cur_x, cur_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            if rect_data["rect_id"]:
                canvas.delete(rect_data["rect_id"])
            rect_data["rect_id"] = canvas.create_rectangle(
                rect_data["start_x"], rect_data["start_y"], cur_x, cur_y, outline="#00ff00", width=2)

        def on_mouse_up(event):
            x1, y1 = rect_data["start_x"], rect_data["start_y"]
            x2, y2 = canvas.canvasx(event.x), canvas.canvasy(event.y)
            left, top_c = min(x1, x2), min(y1, y2)
            right, bottom_c = max(x1, x2), max(y1, y2)
            
            if right - left < 5: return

            cropped = raw_img.crop((left, top_c, right, bottom_c))
            cropped.save("template.png")
            
            self.template_img = cv2.imread("template.png", 0)
            self.lbl_template_status.config(text="Template loaded ✅", foreground="green")
            self.btn_monitor.config(state="normal")
            top.destroy()
            messagebox.showinfo("Success", "Template saved! Now click Start Monitoring.")

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        canvas.image = tk_img

    # --- Monitoring Logic ---
    def toggle_monitoring(self):
        if not self.running:
            self.running = True
            self.btn_monitor.config(text="⏹️ Stop Monitoring")
            self.log("Monitoring started...")
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.running = False
            self.btn_monitor.config(text="▶️ Start Monitoring")
            self.log("Monitoring stopped.")

    def monitor_loop(self):
        while self.running:
            try:
                screen = self.capture_window_area(self.selected_window_hwnd)
                if screen is None:
                    time.sleep(1)
                    continue

                screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                res = cv2.matchTemplate(screen_gray, self.template_img, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                if max_val >= self.confidence_threshold:
                    self.trigger_alert()
                    time.sleep(5) 
            except Exception as e:
                print(f"Monitor Error: {e}")
            time.sleep(self.scan_interval)

    def trigger_alert(self):
        self.log("⚠️ MATCH FOUND! Sending alert...")
        try: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except: pass
        try: notification.notify(title="Dialog Detected!", message="Click now!", timeout=5)
        except: pass

if __name__ == "__main__":
    # Fix High DPI scaling
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    
    root = tk.Tk()
    app = DialogDetectorApp(root)
    root.mainloop()