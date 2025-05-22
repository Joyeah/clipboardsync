import pystray
from pystray import MenuItem as item, Menu
from PIL import Image

# 动态状态
status = "Idle"
selected_option = 1
is_enabled = True

def toggle_status(icon, item):
    global status
    status = "Running" if status == "Idle" else "Idle"
    icon.menu = create_menu()
    icon.update_menu()

def set_option(icon, item, value=None):
    global selected_option
    if value is not None:
        selected_option = value
    icon.update_menu()

def create_menu():
    return (
        item(f"Status: {status}", toggle_status),
        # item("Option 1", lambda icon, item: set_option(icon, item, 1), radio=lambda: selected_option == 1),
        # item("Option 2", lambda icon, item: set_option(icon, item, 2), radio=lambda: selected_option == 2),
        # item("Disabled Item", None, enabled=lambda: is_enabled),
        item("Exit", lambda icon, item: icon.stop(), default=True),
    )

menu = create_menu()
print(menu)
# 创建托盘图标
image = Image.new("RGB", (64, 64), color=(0, 255, 0))
icon = pystray.Icon("test", image, "Menu Example", menu=menu)
icon.run()