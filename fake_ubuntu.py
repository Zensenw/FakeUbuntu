#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fake Ubuntu Screensaver - A Windows screensaver that mimics Ubuntu 18.04 login screen
"""

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import ctypes
import sys
import os

# Try to import PIL for image handling
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration
CONFIG = {
    'password': 'zsw',      # Default password - change this!
    'idle_timeout': 30000,     # 30 seconds idle timeout (milliseconds)
    'hint_timeout': 1300,      # How long to show wrong password hint
    'ubuntu_icon': os.path.join(SCRIPT_DIR, 'src', 'ubuntu_14143.ico'),
    'avatar_icon': os.path.join(SCRIPT_DIR, 'src', 'account_avatar_face_man_people_profile_user_icon_123197.ico'),
    'cancel_icon': os.path.join(SCRIPT_DIR, 'src', 'cancel_close_delete_exit_logout_remove_x_icon_123217.ico'),
    'unlock_icon': os.path.join(SCRIPT_DIR, 'src', 'arrows_chevron_direction_left_move_next_right_icon_123222.ico'),
}

# Try to hide the console window on Windows
if sys.platform == 'win32':
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass


def get_monitors():
    """Get all connected monitors with their positions and sizes"""
    monitors = []

    if sys.platform == 'win32':
        # Windows: use EnumDisplayMonitors
        user32 = ctypes.windll.user32

        # Define callback function type
        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.c_double
        )

        def callback(hmonitor, hdc, rect, data):
            # Get monitor info
            class MONITORINFOEX(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_ulong),
                    ('rcMonitor', ctypes.c_long * 4),  # left, top, right, bottom
                    ('rcWork', ctypes.c_long * 4),
                    ('dwFlags', ctypes.c_ulong),
                    ('szDevice', ctypes.c_wchar * 32)
                ]

            info = MONITORINFOEX()
            info.cbSize = ctypes.sizeof(MONITORINFOEX)
            user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))

            left, top, right, bottom = info.rcMonitor
            monitors.append({
                'x': left,
                'y': top,
                'width': right - left,
                'height': bottom - top,
                'is_primary': info.dwFlags & 1  # MONITORINFOF_PRIMARY
            })
            return 1

        user32.EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)
    else:
        # Fallback: assume single screen
        root = tk.Tk()
        root.withdraw()
        monitors.append({
            'x': 0,
            'y': 0,
            'width': root.winfo_screenwidth(),
            'height': root.winfo_screenheight(),
            'is_primary': True
        })
        root.destroy()

    return monitors


class FakeUbuntuScreensaver:
    def __init__(self):
        # Get all monitors
        self.monitors = get_monitors()

        # Create main window (primary monitor)
        self.root = tk.Tk()
        self.root.title("Ubuntu 18.04")
        self.root.overrideredirect(True)

        # Find primary monitor
        primary = next((m for m in self.monitors if m['is_primary']), self.monitors[0])
        self.root.geometry(f"{primary['width']}x{primary['height']}+{primary['x']}+{primary['y']}")

        # Create windows for additional monitors
        self.secondary_windows = []
        for monitor in self.monitors:
            if not monitor['is_primary']:
                win = tk.Toplevel(self.root)
                win.title("Ubuntu 18.04")
                win.overrideredirect(True)
                win.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['x']}+{monitor['y']}")
                self.secondary_windows.append({'window': win, 'monitor': monitor})

        # Colors - Ubuntu 18.04 style
        self.bg_color = "#300a24"  # Dark purple
        self.bg_gradient_top = "#2c001e"
        self.bg_gradient_bottom = "#300a24"
        self.text_color = "#ffffff"
        self.text_dim_color = "#999999"
        self.hint_color = "#ff5555"
        self.accent_color = "#e95420"  # Ubuntu orange
        self.input_bg = "#3c1e3d"  # Slightly lighter purple for inputs
        self.button_bg = "#452545"

        # Create gradient background canvas for primary window
        self.bg_canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg=self.bg_color
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.after(10, lambda: self.draw_gradient(self.bg_canvas, primary['width'], primary['height']))

        # Configure secondary windows background
        for sw in self.secondary_windows:
            win = sw['window']
            canvas = tk.Canvas(win, highlightthickness=0, bg=self.bg_color)
            canvas.place(x=0, y=0, relwidth=1, relheight=1)
            sw['bg_canvas'] = canvas
            monitor = sw['monitor']
            self.root.after(10, lambda c=canvas, w=monitor['width'], h=monitor['height']: self.draw_gradient(c, w, h))

        # State
        self.is_idle = True
        self.password = ""
        self.hint_text = ""
        self.idle_timer = None
        self.hint_timer = None

        # Hide cursor initially
        self.root.config(cursor="none")
        for sw in self.secondary_windows:
            sw['window'].config(cursor="none")

        # Setup fonts
        self.setup_fonts()

        # Create UI for primary window
        self.create_widgets()

        # Create UI for secondary windows (idle screen only)
        self.create_secondary_widgets()

        # Bind events
        self.bind_events()

        # Start time update
        self.update_time()

        # Start with idle screen
        self.show_idle_screen()

    def draw_gradient(self, canvas, width, height):
        """Draw a vertical gradient on the canvas"""
        canvas.delete("gradient")

        # Calculate steps for smooth gradient
        steps = 100
        for i in range(steps):
            ratio = i / steps
            # Interpolate between top and bottom colors
            r1, g1, b1 = int(self.bg_gradient_top[1:3], 16), int(self.bg_gradient_top[3:5], 16), int(self.bg_gradient_top[5:7], 16)
            r2, g2, b2 = int(self.bg_gradient_bottom[1:3], 16), int(self.bg_gradient_bottom[3:5], 16), int(self.bg_gradient_bottom[5:7], 16)

            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)

            color = f"#{r:02x}{g:02x}{b:02x}"

            y1 = int(height * i / steps)
            y2 = int(height * (i + 1) / steps)

            canvas.create_line(0, y1, width, y1, fill=color, tags="gradient")

    def setup_fonts(self):
        """Setup fonts for the application"""
        # Try common fonts that look similar to Ubuntu
        font_options = ["Segoe UI", "Arial", "Helvetica", "Sans-Serif"]

        self.time_font = tkfont.Font(family=font_options[0], size=96, weight="normal")
        self.date_font = tkfont.Font(family=font_options[0], size=24, weight="normal")
        self.label_font = tkfont.Font(family=font_options[0], size=13, weight="normal")
        self.button_font = tkfont.Font(family=font_options[0], size=11, weight="normal")
        self.name_font = tkfont.Font(family=font_options[0], size=16, weight="bold")
        self.footer_font = tkfont.Font(family=font_options[0], size=28, weight="normal")
        self.header_font = tkfont.Font(family=font_options[0], size=11, weight="normal")
        self.small_font = tkfont.Font(family=font_options[0], size=10, weight="normal")

    def create_widgets(self):
        """Create all UI widgets"""
        # Idle Screen Frame
        self.idle_frame = tk.Frame(self.root, bg=self.bg_color)
        self.idle_frame.place(relx=0.5, rely=0.45, anchor="center")

        # Get current time for initial display
        now = datetime.now()
        initial_time = now.strftime("%H:%M")
        initial_date = now.strftime("%A, %B %d")

        # Idle time label - larger, lighter
        self.idle_time_label = tk.Label(
            self.idle_frame,
            text=initial_time,
            font=self.time_font,
            fg=self.text_color,
            bg=self.bg_color
        )
        self.idle_time_label.pack()

        # Idle date label
        self.idle_date_label = tk.Label(
            self.idle_frame,
            text=initial_date,
            font=self.date_font,
            fg=self.text_color,
            bg=self.bg_color
        )
        self.idle_date_label.pack(pady=(8, 0))

        # Swipe hint
        self.swipe_hint = tk.Label(
            self.idle_frame,
            text="Swipe up to unlock",
            font=self.small_font,
            fg=self.text_dim_color,
            bg=self.bg_color
        )
        self.swipe_hint.pack(pady=(60, 0))

        # Login Screen Frame
        self.login_frame = tk.Frame(self.root, bg=self.bg_color)

        # Top bar - darker with transparency effect
        self.top_bar = tk.Frame(self.login_frame, bg="#1a0510", height=28)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)

        now = datetime.now()
        header_date = now.strftime("%a %b %d")

        self.header_date_label = tk.Label(
            self.top_bar,
            text=header_date,
            font=self.header_font,
            fg=self.text_color,
            bg="#1a0510"
        )
        self.header_date_label.pack(side="left", padx=12, pady=6)

        # Top bar icons - drawn with canvas
        self.icons_frame = tk.Frame(self.top_bar, bg="#1a0510")
        self.icons_frame.pack(side="right", padx=12, pady=6)

        self._draw_topbar_icons()

        # Main login content - centered
        self.login_content = tk.Frame(self.login_frame, bg=self.bg_color)
        self.login_content.pack(expand=True)

        # Inner content frame with some padding
        self.inner_content = tk.Frame(self.login_content, bg=self.bg_color)
        self.inner_content.pack(expand=True)

        # User avatar circle (using canvas for better look)
        self.avatar_canvas = tk.Canvas(
            self.inner_content,
            width=96,
            height=96,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.avatar_canvas.pack(pady=(0, 12))
        # Draw circular avatar background with gradient effect
        self._draw_avatar()

        # User name
        self.name_label = tk.Label(
            self.inner_content,
            text="User",
            font=self.name_font,
            fg=self.text_color,
            bg=self.bg_color
        )
        self.name_label.pack(pady=(0, 16))

        # Password input container - styled like Ubuntu
        self.password_container = tk.Frame(self.inner_content, bg=self.bg_color)
        self.password_container.pack()

        # Password entry with rounded appearance
        self.password_entry = tk.Entry(
            self.password_container,
            font=self.label_font,
            fg=self.text_color,
            bg="#3a1a3b",
            insertbackground=self.text_color,
            show="●",
            width=24,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#5c2d5e",
            highlightcolor=self.accent_color
        )
        self.password_entry.pack(side="left", ipady=6, ipadx=10)

        # Load unlock icon
        self._load_button_icons()

        # Unlock button (next to password field)
        if hasattr(self, 'unlock_icon_img'):
            self.signin_btn = tk.Button(
                self.password_container,
                image=self.unlock_icon_img,
                bg=self.bg_color,
                activebackground=self.bg_color,
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
                command=self.on_signin
            )
        else:
            self.signin_btn = tk.Button(
                self.password_container,
                text="→",
                font=("Segoe UI", 14),
                fg=self.text_color,
                bg=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.text_color,
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                width=3,
                cursor="hand2",
                command=self.on_signin
            )
        self.signin_btn.pack(side="left", padx=(8, 0))

        # Hint label
        self.hint_label = tk.Label(
            self.inner_content,
            text="",
            font=self.label_font,
            fg=self.hint_color,
            bg=self.bg_color
        )
        self.hint_label.pack(pady=(12, 0))

        # Session options at bottom
        self.session_frame = tk.Frame(self.login_content, bg=self.bg_color)
        self.session_frame.pack(side="bottom", pady=20)

        # Ubuntu logo for session
        self.session_canvas = tk.Canvas(
            self.session_frame,
            width=24,
            height=24,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.session_canvas.pack(side="left", padx=(0, 6))
        self._draw_ubuntu_logo_small(self.session_canvas)

        self.session_label = tk.Label(
            self.session_frame,
            text="Ubuntu",
            font=self.small_font,
            fg=self.text_dim_color,
            bg=self.bg_color,
            cursor="hand2"
        )
        self.session_label.pack(side="left")

        # Bottom dock
        self.dock_frame = tk.Frame(self.login_frame, bg=self.bg_color)
        self.dock_frame.pack(side="bottom", fill="x", pady=12)

        # Accessibility and power icons
        self.bottom_left = tk.Label(
            self.dock_frame,
            text="⚙",
            font=self.header_font,
            fg=self.text_dim_color,
            bg=self.bg_color,
            cursor="hand2"
        )
        self.bottom_left.pack(side="left", padx=15)

        self.bottom_right = tk.Label(
            self.dock_frame,
            text="⏻",
            font=self.header_font,
            fg=self.text_dim_color,
            bg=self.bg_color,
            cursor="hand2"
        )
        self.bottom_right.pack(side="right", padx=15)

    def _draw_ubuntu_logo_small(self, canvas):
        """Draw a small Ubuntu logo using icon file"""
        icon_path = CONFIG['ubuntu_icon']
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                self.ubuntu_logo_img = ImageTk.PhotoImage(img)
                canvas.create_image(12, 12, image=self.ubuntu_logo_img)
                return
            except Exception as e:
                print(f"Failed to load ubuntu logo: {e}")
        # Fallback: orange circle
        canvas.create_oval(2, 2, 22, 22, fill=self.accent_color, outline="")

    def _draw_avatar(self):
        """Draw user avatar using icon file"""
        icon_path = CONFIG['avatar_icon']
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                self.avatar_img = ImageTk.PhotoImage(img)
                self.avatar_canvas.create_image(48, 48, image=self.avatar_img)
                return
            except Exception as e:
                print(f"Failed to load avatar: {e}")
        # Fallback: drawn avatar
        self.avatar_canvas.create_oval(4, 4, 92, 92, fill="#3d3d3d", outline="#2d2d2d", width=2)
        self.avatar_canvas.create_oval(12, 12, 84, 84, fill="#4a4a4a", outline="")
        self.avatar_canvas.create_text(48, 48, text="👤", font=("Segoe UI", 38), fill="#cccccc")

    def _draw_topbar_icons(self):
        """Draw top bar icons using canvas"""
        # WiFi icon
        # wifi_canvas = tk.Canvas(self.icons_frame, width=16, height=16, bg="#1a0510", highlightthickness=0)
        # wifi_canvas.pack(side="left", padx=3)
        # wifi_canvas.create_arc(2, 2, 14, 14, start=225, extent=90, style="arc", outline="white", width=1)
        # wifi_canvas.create_arc(4, 4, 12, 12, start=225, extent=90, style="arc", outline="white", width=1)
        # wifi_canvas.create_oval(7, 10, 9, 12, fill="white", outline="")

    def _load_button_icons(self):
        """Load button icons"""
        # Cancel icon
        cancel_icon_path = CONFIG['cancel_icon']
        if os.path.exists(cancel_icon_path):
            try:
                img = Image.open(cancel_icon_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                self.cancel_icon_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load cancel icon: {e}")

        # Unlock icon (arrow)
        unlock_icon_path = CONFIG['unlock_icon']
        if os.path.exists(unlock_icon_path):
            try:
                img = Image.open(unlock_icon_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                self.unlock_icon_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load unlock icon: {e}")

    def create_secondary_widgets(self):
        """Create UI widgets for secondary monitors (idle screen only)"""
        self.secondary_idle_frames = []
        self.secondary_time_labels = []
        self.secondary_date_labels = []

        now = datetime.now()
        initial_time = now.strftime("%H:%M")
        initial_date = now.strftime("%A, %B %d")

        for sw in self.secondary_windows:
            win = sw['window']

            # Idle Screen Frame
            idle_frame = tk.Frame(win, bg=self.bg_color)
            idle_frame.place(relx=0.5, rely=0.45, anchor="center")

            # Idle time label
            time_label = tk.Label(
                idle_frame,
                text=initial_time,
                font=self.time_font,
                fg=self.text_color,
                bg=self.bg_color
            )
            time_label.pack()

            # Idle date label
            date_label = tk.Label(
                idle_frame,
                text=initial_date,
                font=self.date_font,
                fg=self.text_color,
                bg=self.bg_color
            )
            date_label.pack(pady=(8, 0))

            # Swipe hint
            hint_label = tk.Label(
                idle_frame,
                text="Swipe up to unlock",
                font=self.small_font,
                fg=self.text_dim_color,
                bg=self.bg_color
            )
            hint_label.pack(pady=(60, 0))

            self.secondary_idle_frames.append(idle_frame)
            self.secondary_time_labels.append(time_label)
            self.secondary_date_labels.append(date_label)

    def bind_events(self):
        """Bind all events"""
        # Activity detection on primary window
        self.root.bind("<Motion>", self.on_activity)
        self.root.bind("<Key>", self.on_activity)
        self.root.bind("<Button>", self.on_activity)

        # Activity detection on secondary windows
        for sw in self.secondary_windows:
            win = sw['window']
            win.bind("<Motion>", self.on_activity)
            win.bind("<Key>", self.on_activity)
            win.bind("<Button>", self.on_activity)
            win.protocol("WM_DELETE_WINDOW", self.on_close)

        # Password entry
        self.password_entry.bind("<Return>", lambda e: self.on_signin())
        self.password_entry.bind("<Key>", self.on_password_key)

        # Prevent closing with Alt+F4
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_time(self):
        """Update time and date displays"""
        now = datetime.now()

        # Format time
        time_str = now.strftime("%H:%M")
        self.idle_time_label.config(text=time_str)

        # Format date
        date_str = now.strftime("%A, %B %d")
        self.idle_date_label.config(text=date_str)

        # Format header date
        header_date_str = now.strftime("%a %b %d")
        self.header_date_label.config(text=header_date_str)

        # Update secondary monitors
        for time_label in self.secondary_time_labels:
            time_label.config(text=time_str)
        for date_label in self.secondary_date_labels:
            date_label.config(text=date_str)

        # Update every second
        self.root.after(1000, self.update_time)

    def show_idle_screen(self):
        """Show the idle screen with time and date"""
        self.is_idle = True
        self.login_frame.pack_forget()
        self.idle_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.root.config(cursor="none")
        self.clear_password()

        # Show idle screen on secondary monitors
        for idle_frame in self.secondary_idle_frames:
            idle_frame.place(relx=0.5, rely=0.5, anchor="center")
        for sw in self.secondary_windows:
            sw['window'].config(cursor="none")

    def show_login_screen(self):
        """Show the login screen"""
        self.is_idle = False
        self.idle_frame.place_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.root.config(cursor="")
        self.password_entry.focus_set()
        self.reset_idle_timer()

        # Hide idle screen on secondary monitors (show just background)
        for idle_frame in self.secondary_idle_frames:
            idle_frame.place_forget()
        for sw in self.secondary_windows:
            sw['window'].config(cursor="none")

    def on_activity(self, event=None):
        """Handle user activity"""
        if self.is_idle:
            self.show_login_screen()
        else:
            self.reset_idle_timer()

    def on_password_key(self, event):
        """Handle password input"""
        self.hint_label.config(text="")

    def on_signin(self):
        """Handle sign in button click"""
        password = self.password_entry.get()

        if not password:
            return

        if password == CONFIG['password']:
            # Correct password - exit
            self.root.quit()
        else:
            # Wrong password
            self.show_hint("Wrong password!")

    def on_cancel(self):
        """Handle cancel button click"""
        self.clear_password()
        self.show_idle_screen()

    def on_close(self):
        """Handle window close attempt"""
        # Ignore close attempts (like Alt+F4)
        pass

    def show_hint(self, message):
        """Show error hint"""
        self.hint_label.config(text=message)
        if self.hint_timer:
            self.root.after_cancel(self.hint_timer)
        self.hint_timer = self.root.after(
            CONFIG['hint_timeout'],
            lambda: self.hint_label.config(text="")
        )

    def clear_password(self):
        """Clear password entry"""
        self.password_entry.delete(0, tk.END)
        self.hint_label.config(text="")

    def reset_idle_timer(self):
        """Reset the idle timer"""
        if self.idle_timer:
            self.root.after_cancel(self.idle_timer)
        if not self.is_idle:
            self.idle_timer = self.root.after(
                CONFIG['idle_timeout'],
                self.show_idle_screen
            )

    def run(self):
        """Run the screensaver"""
        # Bring all windows to front
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

        for sw in self.secondary_windows:
            win = sw['window']
            win.lift()
            win.attributes("-topmost", True)

        # Run the main loop
        self.root.mainloop()


def create_bat_script():
    """Create a bat script to run the screensaver"""
    bat_content = f'''@echo off
cd /d "{SCRIPT_DIR}"
python fake_ubuntu.py
'''
    bat_path = os.path.join(SCRIPT_DIR, 'run_screensaver.bat')

    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)

    print(f"Created: {bat_path}")
    print("You can copy this file to your desktop for easy access.")
    return bat_path


def main():
    """Main entry point"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['/c', '-c']:
            # Configuration mode - show a simple dialog
            print("Configuration: Edit CONFIG in fake_ubuntu.py to change settings")
            print(f"Current password: {CONFIG['password']}")
            return
        elif arg in ['/p', '-p']:
            # Preview mode - just run normally
            pass
        elif arg in ['/s', '-s']:
            # Screensaver mode - run fullscreen
            pass
        elif arg in ['--create-bat', '-b']:
            # Create bat script
            create_bat_script()
            return

    # Auto-create bat script if it doesn't exist
    bat_path = os.path.join(SCRIPT_DIR, 'run_screensaver.bat')
    if not os.path.exists(bat_path):
        create_bat_script()

    # Create and run the screensaver
    screensaver = FakeUbuntuScreensaver()
    screensaver.run()


if __name__ == "__main__":
    main()
