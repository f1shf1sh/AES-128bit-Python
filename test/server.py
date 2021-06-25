import socket

import time
import threading
import queue
import random
import json  # json.dumps(some)打包   json.loads(some)解包
import logging
import hashlib

IP = '127.0.0.1'
PORT = 9999     # 端口
messages = queue.Queue()
users = []   # 0:userName 1:connection
lock = threading.Lock()

def onlines():    # 统计当前在线人员
    online = []
    for i in range(len(users)):
        online.append(users[i][0])
    return online

class ChatServer(threading.Thread):
    def __init__(self,ip='127.0.0.1',port=9999):
        threading.Thread.__init__(self)
        self.__user_login_info = {}  # this is a dict -> {ip_address<tuple>: name<str>}
        self.__user_msg = list
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_address = (ip,port)

    def __get_serial(self,ip_address):
        port_digest = str(ip_address[1]).encode()
        serial = hashlib.sha1(port_digest).hexdigest()
        return serial[0:6]

    def login(self):
        '''
        检测用户名称是否存在相同
        分三种情况：
        1.用户名不存在（直接添加）
        2.用户名重复（在用户名后添加后缀<哈希编码>，或者提示用户用户名存在）
        3.用户名为空（使用默认用户，全部使用哈希编码方式）
        '''
        DEFAULT_USER_NAME = "用户-"
        try:
            name,ip_address = self.__server_socket.recvfrom(1024)
            name = name.decode('utf-8')

            # 检测用户名是否重复
            for key,value in self.__user_login_info.items():
                # 如果ip地址和名字都相同，则用户一定存在，提示
                if value == name:
                    serial = self.__get_serial(ip_address)
                    name = name + serial

            # 如果name为空
            if name == '':
                serial = self.__get_serial(ip_address)
                name = DEFAULT_USER_NAME + serial
            self.__user_login_info[ip_address] = name
        except:
            logging.warning('login func rcv msg error')
    
    def logout(self):

        '''
        当用户离开聊天室时从字典中删除用户信息
        '''

        pass  
    def rcv_msg(self):
        msg,ip_address = self.__server_socket.recvfrom(1024)
        msg = msg.decode('utf8')
        pass

    def send_msg(self):
        pass

    def server_run(self):
        try:
            self.__server_socket.bind(self.ip_address)
            while True:
                pass

        except:
            logging.warning('server occur error')
    pass


if __name__ == '__main__':
    
    pass