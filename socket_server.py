import wx
from socket import *
import threading  # 创建多线程
from concurrent.futures import ThreadPoolExecutor  # 管理多线程
import struct
import json
import os


class Sever(wx.Frame):
    # 初始化服务器，包括一些GUI组件的初始化
    def __init__(self):
        self.isOn = False  # 表示服务器未启动
        # 开始创建socket服务器对象
        self.server_socket = socket()
        # 创建一个字典，保存所有的客户端
        self.client_thread_dict = {}
        # 创建一个线程池
        self.pool = ThreadPoolExecutor(max_workers=10)
        # 界面布局
        wx.Frame.__init__(self, None, title="基于socket的聊天室", size=(900, 720), pos=(100, 100))  # 初始化父类
        # 创建面板
        self.pl = wx.Panel(self)

        # 创建按钮
        # 启动服务器的按钮
        self.start_server_btn = wx.Button(self.pl, label="启动socket服务器", size=(150, 40), pos=(10, 30))
        # 停止服务器的按钮
        self.stop_server_btn = wx.Button(self.pl, label="停止socket服务器", size=(150, 40), pos=(170, 30))
        # 保存聊天的按钮
        self.save_text_btn = wx.Button(self.pl, label="保存聊天记录", size=(150, 40), pos=(330, 30))
        self.stop_server_btn.Disable()  # 初始时停止按钮不可用

        # 创建客户端列表
        self.client_list = wx.ListBox(self.pl, size=(200, 550), pos=(670, 70),
                                      style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
        wx.StaticText(self.pl, label="已连接客户端:", pos=(670, 40))

        # 创建聊天框
        self.text = wx.TextCtrl(self.pl, size=(650, 550), pos=(10, 70), style=wx.TE_READONLY | wx.TE_MULTILINE)

        # 创建指定的IP地址和端口号的列表
        wx.StaticText(self.pl, label="服务器的IP地址为:", pos=(10, 630))
        self.IP_text = wx.TextCtrl(self.pl, value='127.0.0.1', size=(200, 30), pos=(130, 630), style=wx.TE_MULTILINE)
        wx.StaticText(self.pl, label="服务器的端口号为:", pos=(340, 630))
        self.Port_text = wx.TextCtrl(self.pl, value='62605', size=(200, 30), pos=(460, 630), style=wx.TE_MULTILINE)

        # 给按钮绑定事件
        self.Bind(wx.EVT_BUTTON, self.start_server, self.start_server_btn)  # 启动服务器
        self.Bind(wx.EVT_BUTTON, self.stop_server, self.stop_server_btn)  # 关闭服务器
        self.Bind(wx.EVT_BUTTON, self.save_text, self.save_text_btn)  # 保存聊天记录

    # 启动socket服务器
    def start_server(self, event):
        port_text = self.Port_text.GetValue()
        ip_text = self.IP_text.GetValue()
        if port_text == '' and ip_text == '':
            self.text.AppendText(
                f'---------------请先输入服务器的IP地址和端口号---------------' + '\n')
        else:
            print('启动服务器')
            self.start_server_btn.Disable()
            self.stop_server_btn.Enable()
            # 绑定IP地址和端口号
            self.server_socket.bind((ip_text, int(port_text)))
            # 开启监听
            self.server_socket.listen(8)
            self.text.AppendText(
                f'---------------服务器启动成功---------------IP:{ip_text}---------------端口号为:{port_text}--------------------' + '\n')
            if not self.isOn:
                self.isOn = True
                # 开启线程，保证在服务器监听客户端的同时主程序还能继续运行
                main_thread = threading.Thread(target=self.main_thread_fun)
                # 设置线程为守护线程
                main_thread.daemon = True
                # 开启线程
                main_thread.start()

    # 关闭socket服务器
    def stop_server(self, event):
        if self.isOn:
            self.isOn = False
            self.text.AppendText('---------------正在关闭服务器---------------\n')

            # 关闭所有客户端连接
            for client_name, client_thread in list(self.client_thread_dict.items()):
                try:
                    client_thread.isOn = False
                    client_thread.client_socket.send('服务器即将关闭'.encode('utf8'))
                    client_thread.client_socket.close()
                    self.text.AppendText(f'已断开客户端: {client_name}\n')
                except Exception as e:
                    self.text.AppendText(f'断开客户端{client_name}时出错: {str(e)}\n')

            # 清空客户端字典
            self.client_thread_dict.clear()

            # 关闭服务器socket
            try:
                self.server_socket.close()
                self.text.AppendText('服务器已成功关闭\n')
            except Exception as e:
                self.text.AppendText(f'关闭服务器时出错: {str(e)}\n')

            # 重新创建socket对象以备下次启动
            self.client_thread_dict.clear()  # 清空socket客户端的进程
            self.server_socket = socket()  # 重新创建socket对象以备下次启动

            # 更新UI状态
            wx.CallAfter(self.start_server_btn.Enable)
            wx.CallAfter(self.stop_server_btn.Disable)
            wx.CallAfter(self.client_list.Clear)
            self.text.AppendText('服务器已关闭\n')

    """更新客户端列表显示"""

    def update_client_list(self):
        """更新客户端列表显示"""
        current_clients = list(self.client_thread_dict.keys())
        wx.CallAfter(self.client_list.Set, current_clients)

    # 主线程，用于服务器监听客户端
    def main_thread_fun(self):
        while self.isOn:
            # 在线程里面等待客户端连接
            client_socket, client_addr = self.server_socket.accept()  # 返回的是连接的客户端的socket套接字属性和地址
            client_name = client_socket.recv(1024).decode('utf-8')
            print(client_name)
            # 显示连接信息
            client_thread = ClientThread(client_socket, client_name, self)  # 每个客户端用一个线程来监听
            # 保存到客户端的字典里面
            self.client_thread_dict[client_name] = client_thread
            self.pool.submit(client_thread.run)  # 将每个客户端的线程提交到线程池里面
            self.send(f"[服务器通知]:欢迎{client_name}进入聊天室")
            wx.CallAfter(self.update_client_list)

    def save_text(self, event):
        print('保存聊天记录')
        record = self.text.GetValue()
        with open('record.log', 'a+', encoding='GBK') as f:
            f.write(record)

    def send(self, text):
        """
        这里的send函数和socket对象自带的send函数不一样，这里的send函数直接起到了一个群发的作用
        :param text: 要发送的文本
        :return: 没有返回的参数
        """
        self.text.AppendText(text + '\n')
        offline_clients = []
        for name, client in self.client_thread_dict.items():
            try:
                if client.isOn:
                    client.client_socket.send(text.encode('utf8'))
            except Exception as e:
                print(f"发送失败给 {name}: {str(e)}")
                offline_clients.append(name)
                wx.CallAfter(self.client_list.Delete, self.client_list.FindString(name))
        # 清理已断开客户端
        for name in offline_clients:
            if name in self.client_thread_dict:
                del self.client_thread_dict[name]


# 创建一个类用来保存客户端的线程
class ClientThread(threading.Thread):
    def __init__(self, socket, name, server):
        threading.Thread.__init__(self)  # 父类的初始化
        self.client_socket = socket  # 客户端的socket对象
        self.client_name = name  # 对应的客户端的名称
        self.server = server  # 服务器对象
        self.isOn = True  # 设置当前的客户端的状态

    def receive_file(self, info_size=8096):
        """
        接收客户端上传的文件并保存到服务器的文件夹中
        :param info_size: 一次性接收的数据的大小
        :return: 没有返回的参数
        """
        try:
            # 接收报头长度
            header_size_data = self.client_socket.recv(4)
            if not header_size_data:
                return
            header_size = struct.unpack('i', header_size_data)[0]

            # 接收报头内容
            header_bytes = self.client_socket.recv(header_size)
            header_json = header_bytes.decode('utf-8')
            header_dict = json.loads(header_json)
            filename = header_dict['filename']
            file_size = header_dict['file_size']
            save_path = os.path.join('server_file', filename)
            os.makedirs('server_file', exist_ok=True)

            # 接收文件数据
            received = 0
            with open(save_path, 'wb') as f:
                while received < file_size:
                    data = self.client_socket.recv(info_size)
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
            self.server.send(f'[服务器消息]: 文件 {filename} 上传成功，大小为 {file_size} 字节')
        except Exception as e:
            self.server.send(f'[错误]: 文件接收失败: {str(e)}')

    def send_file(self, filename):
        """
        服务器端主动向客户端发送文件
        """
        try:
            file_path = os.path.join('server_file', filename)  # 获取目标文件的目录
            if not os.path.exists(file_path):
                self.server.send(f'[服务器消息]: 文件 {filename} 不存在！')
                return
            file_size = os.path.getsize(file_path)
            header_dict = {
                'filename': filename,
                'file_size': file_size,
                'md5': 'xxxxxx'  # 你可以用 hashlib.md5() 加密加上真实值
            }
            header_json = json.dumps(header_dict)
            header_bytes = header_json.encode('utf-8')
            header_bytes_len = len(header_bytes)

            # 发送报头长度 + 报头本体
            self.client_socket.send(struct.pack('i',
                                                header_bytes_len))  # 发送报头的长度，这里发送的是报头的长度，第一次发送客户端总是接收不到，不知道为什么，有可能是客户端的线程的原因，使得第一次发送的报头长度被线程接收了，仅仅只是猜测。
            self.client_socket.send(struct.pack('i',
                                                header_bytes_len))  # 面向结果编程01：客户端在接收文件的时候，总是接收不到服务器发送的第一个报头的长度，并且不知道该如何解决，当服务器再发送一次后就可以完美解决这个问题。第一次的报头的长度被客户端的线程接收了，所以要再发送一次。
            self.client_socket.send(header_bytes)  # 发送报头的本体

            # 发送文件内容
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(8096)  # 每次读取8096字节
                    if not data:
                        break
                    self.client_socket.send(data)
            self.server.send(f'[服务器消息]: 文件 {filename} 已成功发送给 {self.client_name}')
        except Exception as e:
            self.server.send(f'[服务器错误]: 文件发送失败: {str(e)}')
            raise  # 重新抛出异常，让上层处理

    def run(self):
        try:
            while self.isOn:
                text = self.client_socket.recv(1024).decode('utf8')
                if not text:  # 客户端主动断开连接
                    raise ConnectionResetError()
                if "断开连接" in text:
                    self.server.send(f'[服务器消息]:{self.client_name}主动离开了聊天室')
                    self.client_socket.close()
                    self.isOn = False
                    if self.client_name in self.server.client_thread_dict:
                        del self.server.client_thread_dict[self.client_name]
                elif 'put' in text:
                    self.server.send(f'[服务器消息]:{self.client_name} 开始上传文件...')
                    self.receive_file()
                elif "get" in text:
                    parts = text.strip().split()
                    if len(parts) == 2:
                        filename = parts[1]
                        self.send_file(filename)
                    else:
                        self.server.send("[服务器消息]: get 命令格式错误，应为：get filename")
                else:
                    self.server.send(f'{self.client_name}消息:{text}')
        except (ConnectionResetError, ConnectionAbortedError):
            self.server.send(f'[服务器消息]:{self.client_name}异常断开连接')
        finally:
            self.close_connection()

    # 关闭掉线的客户端的连接
    def close_connection(self):
        """清除掉掉线的客户端"""
        if self.client_name in self.server.client_thread_dict:
            del self.server.client_thread_dict[self.client_name]
        self.client_socket.close()
        self.isOn = False


if __name__ == "__main__":
    # 创建APP
    app = wx.App()
    # 创建服务器窗口
    sever = Sever()
    # 显示服务器
    sever.Show()
    # 循环显示
    app.MainLoop()
