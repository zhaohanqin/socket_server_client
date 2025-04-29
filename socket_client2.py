import wx
from socket import *
import threading
import os
import struct
import json


class Client(wx.Frame):
    def __init__(self):
        self.name = "客户端02"
        self.isConnected = False  # 客户端是否连接服务器
        self.client_socket = None
        self.download_dir = r"server_file"

        # 界面布局
        wx.Frame.__init__(self, None, title=self.name, size=(560, 750), pos=(800, 100))  # 创建父类初始化
        # 创建面板（窗口）
        self.pl = wx.Panel(self)

        # 创建按钮
        # 1.加入聊天室
        self.conn_btn = wx.Button(self.pl, label="加入聊天室", size=(200, 40), pos=(10, 10))
        # 2.离开聊天室
        self.dis_conn_btn = wx.Button(self.pl, label="离开聊天室", size=(200, 40), pos=(310, 10))
        # 3.清空按钮
        self.clear_btn = wx.Button(self.pl, label="清空消息框", size=(200, 40), pos=(10, 500))
        # 4.发送消息
        self.send_btn = wx.Button(self.pl, label="发送消息", size=(200, 40), pos=(310, 500))
        # 5.创建聊天内容的文本框
        self.text = wx.TextCtrl(self.pl, size=(510, 450), pos=(10, 50), style=wx.TE_READONLY | wx.TE_MULTILINE)
        # 6.创建输入的文本框
        self.input_text = wx.TextCtrl(self.pl, size=(510, 100), pos=(10, 540), style=wx.TE_MULTILINE)
        # 创建指定的IP地址和端口号的列表
        wx.StaticText(self.pl, label="服务器的IP地址为:", pos=(10, 650))
        self.IP_text = wx.TextCtrl(self.pl, value='127.0.0.1', size=(100, 30), pos=(130, 650), style=wx.TE_MULTILINE)
        wx.StaticText(self.pl, label="服务器的端口号为:", pos=(240, 650))
        self.Port_text = wx.TextCtrl(self.pl, value='62605', size=(100, 30), pos=(360, 650), style=wx.TE_MULTILINE)

        # 将按钮和事件相互绑定
        self.Bind(wx.EVT_BUTTON, self.conn, self.conn_btn)  # 加入聊天室
        self.Bind(wx.EVT_BUTTON, self.dis_conn, self.dis_conn_btn)  # 离开聊天室
        self.Bind(wx.EVT_BUTTON, self.clear, self.clear_btn)  # 清空消息框
        self.Bind(wx.EVT_BUTTON, self.send, self.send_btn)  # 发送消息

    # 注意,创建事件的时候不能再__init__初始化里面创建事件
    # 加入聊天室的事件
    def conn(self, event):
        port_text = self.Port_text.GetValue()
        ip_text = self.IP_text.GetValue()
        if port_text == '' and ip_text == '':
            self.text.AppendText(
                f'---------------请先输入服务器的IP地址和端口号---------------' + '\n')
        else:
            if not self.isConnected:
                print(f"{self.name}加入了聊天室")
                self.isConnected = True
                self.client_socket = socket()  # 在客户端创建一个socket实例，
                self.client_socket.connect((ip_text, int(port_text)))  # 用于连接服务器,服务器的地址和端口号用元组表示
                # 客户端发送消息
                self.client_socket.send(self.name.encode('utf8'))

                # 接受服务器的消息
                main_thread = threading.Thread(target=self.rec_data)
                main_thread.daemon = True
                main_thread.start()

    def rec_data(self):
        """
        客户端接收服务器端发送过来的消息
        :return: 没有返回的参数
        这里有个bug，就是在客户端和服务器端进行文件参数的时候，当服务器向客户端发送文件的时候，客户端这里最开始会收到一个报头长度的数据，所以后续显示的时候，接收文件后的服务器通知会有点不一样。
        """
        while self.isConnected:
            text = self.client_socket.recv(1024).decode('utf8')
            if '服务器即将关闭' in text:
                self.isConnected = False
                self.client_socket.close()
                self.text.AppendText(text + '\n')
            else:
                self.text.AppendText(text + '\n')

    # 离开聊天室的事件
    def dis_conn(self, event):
        print(f"{self.name}离开了聊天室")
        self.client_socket.send(f'{self.name}断开连接了'.encode("utf8"))
        self.text.AppendText(f'{self.name}断开连接了' + '\n')
        self.isConnected = False
        self.client_socket.close()

    # 清空消息框的事件
    def clear(self, event):
        print(f"{self.name}清空了消息框")
        self.input_text.Clear()

    def send_to_server(self, cmd):
        """
        客户端将文件发送到服务器上面储存下来
        :param self: 客户端的socket对象
        :param cmd: 用户在客户端输入的文本，包含文件的名称。例：put 2.docx
        :return: 没有返回
        """
        cmd = cmd.split()
        filename = cmd[1]
        file_path = os.path.join('client_file', filename)  # 获取要发送给服务器的文件的路径
        # 以读的方式打开文件，读取文件内容上传给服务器
        # 第一步: 制作报头
        header_dic = {
            'filename': filename,
            'md5': 'xxxxxxx',
            'file_size': os.path.getsize(file_path)
        }
        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')
        # 第二步: 先发送报头长度
        self.client_socket.send(struct.pack('i', len(header_bytes)))
        # 第三步: 再发报头
        self.client_socket.send(header_bytes)
        # 第四步: 再发送真实数据
        with open(file_path, 'rb') as f:
            send_size = 0
            for line in f:
                self.client_socket.send(line)
                # 下面的作用是显示出发送文件的进度
                send_size += len(line)
                print(((send_size / header_dic['file_size']) * 100), '%')

    def get_from_server(self, info_size=8096):
        """
        客户端从服务器端下载对应的文件
        :param info_size: 接收的数据的大小
        :return: 没有返回的参数
        """
        try:
            # 第一步: 先收报头的长度
            header_size_data = self.client_socket.recv(4)
            if not header_size_data:
                return
            header_size = struct.unpack('i', header_size_data)[0]

            # 第二步: 再收报头
            header_bytes = self.client_socket.recv(header_size)
            if not header_bytes:
                return

            # 第三步: 从报头中解析出对真实数据的描述信息
            header_json = header_bytes.decode('utf-8')
            header_dic = json.loads(header_json)
            filename = header_dic['filename']
            file_size = header_dic['file_size']
            save_path = os.path.join('client_file', filename)
            os.makedirs('client_file', exist_ok=True)

            # 第四步: 接收真实的数据
            received = 0
            with open(save_path, 'wb') as f:
                while received < file_size:
                    data = self.client_socket.recv(info_size)
                    if not data:
                        break
                    f.write(data)
                    received += len(data)  # 计算真实的接收长度，如果以后增加打印进度条的时候就可以精确无误的表示
                    print(int((received / file_size) * 100), '%')
        except Exception as e:
            self.text.AppendText(f'下载文件时出错: {str(e)}\n')

    # 发送消息
    def send(self, event):
        print(f"{self.name}发送了消息")
        if self.isConnected:
            text = self.input_text.GetValue()
            if text != '':
                if text != '断开连接':
                    # 客户端向服务器端发送文件
                    if "put" in text:
                        self.client_socket.send(text.encode('utf8'))
                        self.send_to_server(text)
                        self.input_text.Clear()
                    if "get" in text:
                        self.client_socket.send(text.encode('utf8'))
                        self.get_from_server()
                        self.input_text.Clear()
                    else:
                        self.client_socket.send(text.encode('utf8'))
                        self.input_text.Clear()
                else:
                    self.client_socket.send(text.encode('utf8'))
                    self.text.AppendText(f"{self.name}断开连接了" + '\n')
                    self.isConnected = False
                    self.client_socket.close()
                    self.input_text.Clear()


if __name__ == '__main__':
    # 创建应用程序对象
    app = wx.App()
    # 创建客户端窗口
    client = Client()
    # 显示客户端的窗口
    client.Show()
    # 循环显示
    app.MainLoop()
