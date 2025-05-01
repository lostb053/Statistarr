# MIT License
# Copyright (c) 2025 LostB053
# See LICENSE file in the project root for full license text.

import sys
import time
import atexit
import subprocess
from PIL import Image
from pystray import Icon, Menu, MenuItem


# Function to start fetcher
def start_fetcher():
    global fetcher_process
    if fetcher_process is None or fetcher_process.poll() is not None:
        fetcher_process = subprocess.Popen('fetcher.exe')


# Function to stop fetcher
def stop_fetcher():
    global fetcher_process
    if fetcher_process and fetcher_process.poll() is None:
        fetcher_process.terminate()
        fetcher_process = None


# Function to launch the stats viewer
def launch_stats():
    subprocess.Popen(['python', 'statistarr.py'])


# Function to launch the chart viewer
def launch_chart():
    subprocess.Popen(['python', 'cchart.py'])


# Function to check if fetcher is running
def is_fetcher_running(item = None):
    return fetcher_process is not None and fetcher_process.poll() is None


# Function to toggle fetcher state
def toggle_fetcher(icon, item):
    if is_fetcher_running(item):
        stop_fetcher()
    else:
        start_fetcher()
    icon.update_menu()  # Forces the tray to refresh menu state


def update_fetcher_state():
    global toggle
    # Check if the fetcher state has changed
    if is_fetcher_running() != toggle:
        toggle = is_fetcher_running()
        return True
    return False


# Function for tray icon and menu
def create_tray_icon():
    icon = Icon("Statistarr", Image.open("icon.ico"))
    icon.title = "Statistarr"
    tray_menu = Menu(
        MenuItem("Open Stats Viewer", lambda icon, item: launch_stats()),
        MenuItem("Open QuickChart Generator", lambda icon, item: launch_chart()),
        MenuItem("Toggle Fetcher", toggle_fetcher, checked=is_fetcher_running),
        MenuItem("Exit", exit_app)
    )
    icon.menu = tray_menu
    icon.run_detached()
    start_fetcher()  # Start fetcher when the tray icon is created
    while True:
        global toggle
        if update_fetcher_state():
            icon.update_menu()  # Update tray icon if fetcher state has changed
        time.sleep(1)  # Check every second (you can adjust the interval as needed)
        if not icon.visible:
            break  # Exit the loop if the icon is not visible


# Function to exit the tray app
def exit_app(icon, item):
    if fetcher_process and fetcher_process.poll() is None:
        fetcher_process.terminate()
    icon.visible = False  # Hide the icon
    icon.stop()


# Register the safe exit function to ensure fetcher is terminated on exit
def safe_exit():
    if fetcher_process and fetcher_process.poll() is None:
        fetcher_process.terminate()


if __name__ == '__main__':
    fetcher_process = None  # Global variable to keep track of fetcher process
    toggle = False  # Global variable to keep track of fetcher state
    atexit.register(safe_exit)  # Register the safe exit function
    create_tray_icon() # Start the tray icon
