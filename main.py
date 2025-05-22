'''
通过udp协议接收数据；通过热键监听器获取剪贴板内容，并发送给其它UDP服务器；

本程序启动三个线程：
1. 托盘图标线程
2. UDP服务器线程
3. 全局热键监听线程
'''
import argparse
import ipaddress
import pystray
from PIL import Image, ImageDraw
import threading
import socket
from pynput import keyboard
import pyperclip

from iptools import scan_udpserver_multithread


starting = False  # 用于标记是否已经启动
# UDP服务器
my_ip = socket.gethostbyname(socket.gethostname())
print(f"My IP address: {my_ip}")
port = 5005
buffer_size = 1024  # 接收数据的最大尺寸
# UDP客户端列表
clients = []  # 用于存储已连接的客户端地址

def find_client_address():
    global clients
    # 假设子网掩码为24位，即/24，可以根据实际情况调整
    network = ipaddress.ip_network(f"{my_ip}/24", strict=False)

    print("Starting network scan...")
    clients = scan_udpserver_multithread(network.hosts(), port=port)
    print(f"Active IPs found on port {port}: {clients}")
    
def add_to_clients(ip:str):
    global clients
    if clients.count(ipaddress.IPv4Address(ip)) == 0:
        clients.append(ipaddress.IPv4Address(ip))
def remove_from_clients(ip:str):
    global clients
    if clients.count(ipaddress.IPv4Address(ip)) > 0:
        clients.remove(ipaddress.IPv4Address(ip))

# 创建一个简单的图标图像（也可以用本地图片文件）
def create_image():
    # 创建一个简单的彩色图标
    image = Image.new('RGB', (64, 64), (255, 0, 255))  # 黄色背景
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(0, 128, 255))  # 蓝色方块
    return image

# 显示所有UDP客户端
def show_clients(icon, item):
    print(clients)
    

# 托盘图标点击事件
def on_scan(icon, item):
    print(f"Menu item '{item}' clicked：scan udp client address")
    find_client_address()


# 退出程序
def exit_program(icon, item):
    print("Exiting pystray...")
    icon.stop()
    print("Exiting hotkey listener...")
    listener.stop()  # 停止热键监听器
    print("Exiting UDP server...")
    starting = False  # 设置为False，表示已经退出
    


# 启动系统托盘图标（运行在主线程之外）
def run_systray():
    image = create_image()

    menu = (
        pystray.MenuItem('Show Clients', show_clients),
        pystray.MenuItem('Scan', on_scan),
        pystray.MenuItem('Exit', exit_program)
    )

    icon = pystray.Icon("test_icon", image, "ClipboardSync", menu)
    icon.run()


def start_udp_server():
    global clients
    # 启动UDP服务器
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # try:
            sock.bind((my_ip, port))
            print(f"UDP server started on {my_ip}:{port}")
            # 设置非阻塞模式
            sock.setblocking(False)
            while starting:
                try:
                    data, address = sock.recvfrom(buffer_size)
                    msg = data.decode()
                    print(f"Received from {address}: {msg}")
                    # 向客户端发送响应
                    if msg == "ping":
                        response = "pong"
                        print(f"Reply {address}: {response}")
                        sock.sendto(response.encode(), address)
                        # add to clients
                        add_to_clients(address[0])
                    else:
                        # response = f"Server received: {msg}"
                        # sock.sendto(response.encode(), address)
                        # 处理接收到的数据, 写入剪贴板
                        pyperclip.copy(msg)
                        print(f"Clipboard updated with: {msg}")

                except BlockingIOError:
                    continue
        # except Exception:
        #     starting = False
            

def on_hotkey_active():
    global clients
    # print('Global hotkey activated!')
    clipboard_content = pyperclip.paste()
    print(f'Send Clipboard content: {clipboard_content}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for client in clients:
            # 发送剪贴板内容到每个客户端
            try:
                chost = str(client)
                if chost == my_ip:
                    continue
                print(f"Sending to {chost}:{port}")
                sock.sendto(clipboard_content.encode(), (chost, port))
                print(f"Sent to {chost}:{port}: {clipboard_content}")
            except Exception as e:
                print(f"Error sending to {client}: {e}")
                continue
        

def for_canonical(f):
    return lambda k: f(listener.canonical(k))


# 主程序中启动托盘图标作为一个线程
if __name__ == "__main__":
    # 初始化全局变量
    parser = argparse.ArgumentParser(description="UDP Clipboard Sync")
    parser.add_argument('-p', '--port', type=int, default=5005, help='UDP port to listen on （default 5005）')
    args = parser.parse_args()
    port = args.port

    starting = True  # 设置为True，表示已经启动
    # 1. 启动托盘图标
    systray_thread = threading.Thread(target=run_systray)
    systray_thread.daemon = True  # 设置为守护线程
    systray_thread.start()
    print("System tray icon is running...")

    # 2. 启动UDP服务器
    udp_server_thread = threading.Thread(target=start_udp_server)
    udp_server_thread.daemon = True  # 设置为守护线程
    udp_server_thread.start()
    print("UDP server is running...")

    # 3. 查找客户端地址
    threading.Thread(target=find_client_address).start()
    print("Finding client address...")
    # TODO 定时检测客户端
    

    # 4. 启动全局热键监听
    hotkey = keyboard.HotKey(keyboard.HotKey.parse('<ctrl>+<alt>+v'), on_hotkey_active)
    with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as listener:
        print("Global hotkey listener is running...")
        listener.join()
