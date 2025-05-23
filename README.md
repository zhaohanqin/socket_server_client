# socket_server_client
**一个基于python的socket服务器的搭建（同时包含了socket客户端的搭建）**，实现的效果为一个可以通过IP和端口号对服务器进行连接的聊天室。   
由于用到的都是python的内置的库，所以也就不用下载新的包。  
由于现在的我对于socket服务器端的一些代码还是有点不够了解，后续待我了解以后会进行相应的更新。

# socket服务器端
***在这里建立了socket服务器，完成的功能是接收从客户端发来的消息***，然后把该消息加上对应的客户端的名字，在服务器区进行广播。  
1. 服务器端的主线程主要是运行的是服务器对象。
   - 无序标题1
   - 无序标题2
     - 无序标题3
2. 然后与客户端进行连接后，返回的是客户端对象与客户端的地址
```python
client_socket, client_addr = self.server_socket.accept()  # 返回的是连接的客户端的socket套接字属性和地址
```
服务器进行接收客户端的消息就是靠client_socket对象接收客户端发送的消息的，所以在有多个客户端的情况下，可能只能接受完一个客户端的消息，因此就应该对于每一个客户端对象来说就应该为其再创建一个新的线程，未来保持后续可以接受其他的客户端发来的消息。  
相应的代码如下所示：
```python
client_thread = ClientThread(client_socket, client_name, self)  # 每个客户端用一个线程来监听
self.client_thread_dict[client_name] = client_thread # 保存到客户端的字典里面
self.pool.submit(client_thread.run)  # 将每个客户端的线程提交到线程池里面
self.send(f"[服务器通知]:欢迎{client_name}进入聊天室")
wx.CallAfter(self.update_client_list)
```
后续在服务器端添加了和客户端传输文件的功能。

# socket客户端
> 主要实现的功能就是和服务器建立连接，然后把服务器广播的消息显示在消息池里面，同时还可以发送消息给服务器。
>
> 引用里面嵌套代码块。
> ```python
> a = input("请输入想要数据")  # input得到的只能是字符串
> print(type(a))
> b = eval(input("请输入想要数据"))  # eval()函数可以自动地去判断输入的数据的类型然后进行相应的转换
> print(type(b))
> ```
>
> 这里的引用换行还是需要按两次换行键

后续在客户端添加了和服务器端传输文件的功能。  
![图片](https://api.zzzmh.cn/v2/bz/v3/getUrl/a202c44c2075478dbfac39baeb80004610)  
<img style="width:1000px;" src="https://api.zzzmh.cn/v2/bz/v3/getUrl/a202c44c2075478dbfac39baeb80004610">
![图片](https://haowallpaper.com/link/common/file/previewFileImg/16773548007017856)  
但是这里有个小bug，就是客户端接收文件的时候，由于客户端的多线程接收操作，服务器发送的报头的长度会被客户端的多线程接收功能接收到，所以接收文件里面最开始接收的报头长度就不对了，所以我在服务器端将报头的长度发送了两遍，这样客户端接收文件的的函数里面就会接收到准确的报头长度了。
