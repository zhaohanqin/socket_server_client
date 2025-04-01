# socket_server_client
一个基于python的socket服务器的搭建（同时包含了socket客户端的搭建），实现的效果为一个可以通过IP和端口号对服务器进行连接的聊天室
由于用到的都是python的内置的库，所以也就不用下载新的包。
由于现在的我对于socket服务器端的一些代码还是有点不够了解，后续待我了解以后会进行相应的更新

# socket服务器端
在这里建立了socket服务器，完成的功能是接收从客户端发来的消息，然后把该消息加上对应的客户端的名字，在服务器区进行广播
服务器端的主线程主要是运行的是服务器对象
然后与客户端进行连接后，返回的是客户端对象与客户端的地址
client_socket, client_addr = self.server_socket.accept()  # 返回的是连接的客户端的socket套接字属性和地址
服务器进行接收客户端的消息就是靠client_socket对象接收客户端发送的消息的，所以在有多个客户端的情况下，可能只能接受完一个客户端的消息，因此就应该对于每一个客户端对象来说就应该为其再创建一个新的线程，未来保持后续可以接受其他的客户端发来的消息。
相应的代码如下所示：
client_thread = ClientThread(client_socket, client_name, self)  # 每个客户端用一个线程来监听
self.client_thread_dict[client_name] = client_thread # 保存到客户端的字典里面
self.pool.submit(client_thread.run)  # 将每个客户端的线程提交到线程池里面
self.send(f"[服务器通知]:欢迎{client_name}进入聊天室")
wx.CallAfter(self.update_client_list)

# socket客户端
主要实现的功能就是和服务器建立连接，然后把服务器广播的消息显示在消息池里面，同时还可以发送消息给服务器。
