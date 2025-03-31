import wx
from socket import *
import threading


class Client(wx.Frame):
    def __init__(self):
        self.name = "客户端01"
        self.isConnected = False  # 客户端是否连接服务器
        self.client_socket = None

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
                main_thread = threading.Thread(target=self.recv_data)
                main_thread.daemon = True
                main_thread.start()

    def recv_data(self):
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

    # 发送消息
    def send(self, event):
        print(f"{self.name}发送了消息")
        if self.isConnected:
            text = self.input_text.GetValue()
            if text != '':
                if text != '断开连接':
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
