# 剪切板同步工具

## 依赖

- 系统托盘图标(pystray)
- 全局热键监听(pynput.keyboard)
- 剪切板操作(pyperclip)
- UDP服务器(socket)

## 功能
- 系统托盘图标
- UDP服务端
- 全局热键监听（Ctrl+Alt+V）
- 启动时自动发现局域网内其他同步端
- 手动扫描局域网内其他同步端
- 当收到其它同步端时，自动添加到剪切板同步列表
- 通知接收到新剪切板内容
- TODO: 剪切板自动同步功能


## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py  
```
or 
```bash
python main.py --port 12345
```

## 使用说明

Press Crtl+Alt+V to sync clipboard
