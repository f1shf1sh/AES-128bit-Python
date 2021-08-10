import sys
import json
import time
import binascii
from Crypto.Crypto import AES
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

server_ui_file_path = "..\\Python\\qt5\\xml\\Server.ui"

class Server(QWidget):
    def __init__(self):
        super(Server, self).__init__()
        self.aes = AES(b'+~\x15\x16(\xae\xd2\xa6\xab\xf7\x15\x88\t\xcfO<')
        self.RobotName = 'Siri'
        self.ui = uic.loadUi(server_ui_file_path)
        self.InitNetWork()
        self.ui.show()

    def InitNetWork(self):
        self.sock = QUdpSocket(self)
        self.sock.bind(QHostAddress.LocalHost, 8888)
        self.sock.readyRead.connect(self.RecvMsg)

    def SyncTableWidget(self, ItemList):
        CurRowCounts = self.ui.tableWidget.rowCount()
        CurRowCounts += 1
        self.ui.tableWidget.setRowCount(CurRowCounts)
        for col in range(len(ItemList)):
            NewItem = QTableWidgetItem(ItemList[col])
            self.ui.tableWidget.setItem(CurRowCounts-1, col, NewItem)
        
    def RecvMsg(self):
        while self.sock.hasPendingDatagrams():
            Datagram, Host, Port = self.sock.readDatagram(
                self.sock.pendingDatagramSize()
            )
        ItemList = self.UnpackMsg(Datagram)
        self.SyncTableWidget(ItemList)
        self.SendMsg(ItemList[2])

    def SendMsg(self, Msg):
        TIME = ['Time', '时间', 'time']
        SendMsg = 'Hello! ヾ(•ω•`)o'
        EncJsonStr = self.PackMsg(SendMsg)
        self.sock.writeDatagram(EncJsonStr, QHostAddress.LocalHost, 9999)

    def UnpackMsg(self, EncJsonStr):
        JsonStr = self.aes.decrypt(EncJsonStr).decode('utf-8').strip().strip(b'\x00'.decode())
        InfoDict = json.loads(JsonStr)
        EncMsg = InfoDict['EncMsg']
        Msg = self.aes.decrypt(binascii.a2b_hex(EncMsg.encode('utf-8'))).decode('utf-8')
        Date = InfoDict['Date']
        return [Date, EncMsg, Msg]
    
    def PackMsg(self, Msg):
        RobotName = self.RobotName
        Date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        EncMsg = binascii.b2a_hex(self.aes.encrypt(Msg.encode("utf-8"))).decode()
        MsgDict = {
            "Name": RobotName,
            "EncMsg": EncMsg,
            "Date": Date
        }
        JsonStr = json.dumps(obj=MsgDict)
        EncJsonStr = self.aes.encrypt(JsonStr.encode('utf-8'))
        return EncJsonStr

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = Server()
    app.exec_()