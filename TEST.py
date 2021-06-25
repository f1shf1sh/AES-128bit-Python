from NetWork import Server
from Cryptodome.Cipher import AES
import random
import hashlib
import time
# server = Server(ip_address = '127.0.0.1', port = 9999)
# server.create_server(5)
plain = b'2C\xf6\xa8\x88Z0\x8d11\x98\xa2\xe07\x074'
key = b'+~\x15\x16(\xae\xd2\xa6\xab\xf7\x15\x88\t\xcfO<'
aes = AES.new(key, AES.MODE_ECB)
print(aes.encrypt(plain))