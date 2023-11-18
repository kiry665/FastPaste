import keyboard
import subprocess
def on_hotkey_press():
    subprocess.Popen(['python3', 'main.py'])

keyboard.add_hotkey('ctrl+i', on_hotkey_press)
keyboard.wait('esc')