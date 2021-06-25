import socket
import sys

class Socket(object):
    # init socket class
    # default port is 9999, ip address is '127.0.0.1'
    def __init__(self,ip_address="localhost",port=9999):
        self.__ip_address = ip_address
        self.__port = port
        self.__socket = self.create_socket()
    # create socket
    def create_socket(self):
        # family, socket type, communication protocol
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,socket.IPPROTO_TCP)
        return _socket

    def get_ip_address(self):
        self.__ip_address = self.__socket.gethostname()
    
    def connect(self):
        self.__socket.connect(self.__ip_address,self.__port)
    
    def set_listener(self,listen_num):
        
        self.__socket.listen(listen_num)
        return self.__socket
    
    def socket_bind(self):
        self.__socket.bind((self.__ip_address,self.__port))
        return self.__socket

class Server():
    pass
    
class Client():

    pass


    