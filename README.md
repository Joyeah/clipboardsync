# clipboard sync tools

## Dependencies

- Pystray: System Tray Icon in Python
- pynput：listen mouse & keyboard keys
- pyperclip: a cross-platform Python module for copy and paste clipboard functions.
- socket: UDP server and client

## Functions
- system tray icon
- UDP server
- Global hotkey listener（Ctrl+Alt+V）
- automatic find udp clents(Scan at starting)
- show udp clients
- When recive a new client's message, then add to list.
- notice when recive a new client's message.
- auto sync clipboard （v1.0.1)
- TODO: hotkey to exist the program
- TODO: hotkey to switch automatic sync clipboard


## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```
or 
```bash
python main.py --port 12345
```

## Usage

Press Crtl+Alt+V to sync clipboard

## Screenshots

![screenshot1](./screenshot0.png)
![screenshot2](./screenshot1.png)
