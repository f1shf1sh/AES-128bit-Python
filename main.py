import sys
import json
import time
import binascii
from Crypto.Crypto import AES
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QUdpSocket, QHostAddress
from PyQt5 import uic

wechat_ui_file_path = 'qt5\\xml\\WeChat.ui'
login_ui_file_path = 'qt5\\xml\\Login.ui'

class Login():
    def __init__(self):
        self.ui = uic.loadUi(login_ui_file_path)
        self.InitSign()
        self.ShowLoginWindow()
    
    def ShowLoginWindow(self):
        self.ui.show()

    def InitSign(self):
        self.ui.pushButton.clicked.connect(self.GetUserName)
        self.ui.pushButton.clicked.connect(self.ui.close)

    def GetUserName(self) -> str:
        self.UserName = self.ui.lineEdit.text()
        # if self.UserName == '':
        #     QMessageBox.warning(QWidget, 
        #     "警告",
        #     "用户名不能为空!",
        #     QMessageBox.Yes)
        print(self.UserName)
        
        

class WeChat():
    def __init__(self, UserName):
        self.aes = AES(b'+~\x15\x16(\xae\xd2\xa6\xab\xf7\x15\x88\t\xcfO<')
        self.UserName = UserName
        self.ui = uic.loadUi(wechat_ui_file_path)
        self.TCP_HOST = '127.0.0.1'
        self.TCP_PORT = 9999
        self.InitSign()
        self.InitNetWork(self.TCP_HOST, self.TCP_PORT)
        self.ShowMainWindow()
        
    def ShowMainWindow(self):
        self.ui.show()

    def InitNetWork(self, ipAddress, Port):
        self.sock = QUdpSocket()
        self.sock.bind(QHostAddress.LocalHost, Port)
        self.sock.readyRead.connect(self.RecvMsg)

    def InitSign(self):
        self.ui.pushButtonSend.clicked.connect(self.SendMsg)
        self.ui.pushButtonExit.clicked.connect(self.ui.close)

    def PackMsg(self, Msg) -> str:
        UserName = self.UserName
        Date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        self.ShowMsg(self.UserName, Msg, Date)
        EncMsg = binascii.b2a_hex(self.aes.encrypt(Msg.encode("utf-8"))).decode()
        MsgDict = {
            "Name": UserName,
            "EncMsg": EncMsg,
            "Date": Date
        }
        JsonStr = json.dumps(obj=MsgDict)
        EncJsonStr = self.aes.encrypt(JsonStr.encode('utf-8'))
        return EncJsonStr

    def UnpackMsg(self, EncJsonStr):
        JsonStr = self.aes.decrypt(EncJsonStr).decode('utf-8').strip().strip(b'\x00'.decode())
        InfoDict = json.loads(JsonStr)
        EncMsg = InfoDict['EncMsg']
        RobotName = InfoDict['Name']
        Msg = self.aes.decrypt(binascii.a2b_hex(EncMsg.encode('utf-8'))).decode('utf-8')
        Date = InfoDict['Date']
        return RobotName, Msg, Date

    def SendMsg(self):
        Msg = self.ui.plainTextEdit.toPlainText()
        self.ui.plainTextEdit.clear()
        if Msg == '':
            Msg = 'None'
        EncJsonStr = self.PackMsg(Msg)
        self.sock.writeDatagram(EncJsonStr, QHostAddress.LocalHost, 8888)
        

    def ShowMsg(self, UserName, Msg, Date):
        self.ui.textBrowser.setTextColor(Qt.blue)
        self.ui.textBrowser.setCurrentFont(QFont("微软雅黑", 12))
        self.ui.textBrowser.append('【'+UserName+'】' + Date)
        self.ui.textBrowser.append('  '+Msg)

    def RecvMsg(self):
        while self.sock.hasPendingDatagrams():
            Datagram, Host, Port = self.sock.readDatagram(
                self.sock.pendingDatagramSize()
                )
            RobotName, Msg, Data = self.UnpackMsg(Datagram)
            self.ShowMsg(RobotName, Msg, Data)
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # login = Login()
    wechat = WeChat('Fish')
    app.exec_()