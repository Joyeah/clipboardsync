import socket
import ipaddress
from tqdm import tqdm

def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        my_ip = s.getsockname()[0]
    except Exception:
        my_ip = '127.0.0.1'
    finally:
        s.close()

    return my_ip

def scan_port(ip, port=80, timeout=0.5):
    """
    尝试连接指定IP和端口。
    
    :param ip: 目标IP地址
    :param port: 目标端口号，默认为80
    :param timeout: 超时时间，默认为0.5秒
    :return: 如果成功连接返回True，否则返回False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return True
        except (socket.timeout, socket.error):
            return False
        
def scan_udp_port(ip, port=5005, timeout=0.5):
    '''通过UDP协议扫描指定IP和端口'''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(b"ping", (ip, port))
            data, addr = sock.recvfrom(1024)
            return True
        except (socket.timeout, socket.error):
            return False
        

def scan_network(ip_range, port=80):
    """
    遍历网络范围并扫描每个IP地址的指定端口。
    
    :param ip_range: IP地址生成器或列表
    """
    active_ips = []
    with tqdm(total=254, desc="Scanning", unit="IP") as pbar:
        for ip in ip_range:
            pbar.set_description(f"Scanning {ip}")
            pbar.update(1)
            if scan_port(str(ip), port):
                # print(f"{ip} has port {port} open.")
                active_ips.append(ip)
            else:
                pass  # Port is closed or host is down
    return active_ips

def scan_udpserver_multithread(ip_range, port=80):
    """
    使用多线程扫描网络中的UDP server, 并返回IP列表。
    
    :param ip_range: IP地址生成器或列表
    """
    import concurrent.futures
    active_ips = []
    with tqdm(total=254, desc="Scanning", unit="IP") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_ip = {executor.submit(scan_udp_port, str(ip), port): ip for ip in ip_range}
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                pbar.set_description(f"Scanning {ip}")
                pbar.update(1)
                if future.result():
                    active_ips.append(ip)
    return active_ips
    

if __name__ == "__main__":
    # 获取本机IP地址，并构建对应的IP网络范围
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        my_ip = s.getsockname()[0]
    except Exception:
        my_ip = '127.0.0.1'
    finally:
        s.close()
    print(f"My IP address: {my_ip}")

    # 假设子网掩码为24位，即/24，可以根据实际情况调整
    network = ipaddress.ip_network(f"{my_ip}/24", strict=False)

    print("Starting network scan...")
    port = 5005
    active_ips = scan_udpserver_multithread(network.hosts(), port=port)
    print(f"Active IPs found on port {port}: {active_ips}")