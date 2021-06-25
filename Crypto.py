from AES_box import S_BOX, L_SBOX, RCON
import copy
import binascii

class AES():
    def __init__(self ,key):
        self.__key = key
        self.__key_state_matrix = None
        self.__msg_state_matrix = None
        self.__s_box = S_BOX
        self.__l_sbox = L_SBOX
        self.__Rcon = RCON
        self.N = 4
        self.__key_state_matrix = self.__key_extension(self.__key)
        
    def __add_round_key(self, msg_state, key_state):
        for row in range(self.N):
            for col in range(self.N):
                msg_state[col][row] ^= key_state[col][row]  

    def __sub_bytes(self, state):
        for row in range(self.N):
            for col in range(self.N):
                state[row][col] = self.__s_box[state[row][col]>>4][state[row][col]&0x0F]

    def __shift_rows(self, state):
        shift_num = 1
        for row in range(1, self.N):
            for _ in range(shift_num):
                byte = state[row][0]
                for n in range(self.N - 1):
                    state[row][n] = state[row][n+1]
                state[row][3] = byte
            shift_num += 1

    def __mix_columns(self, state):
        mix_matrix =[[0x02, 0x03, 0x01, 0x01],
                     [0x01, 0x02, 0x03, 0x01],
                     [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]]
        temp_state_matrix = copy.deepcopy(state)

        for row in range(self.N):
            for col in range(self.N):
                product = 0
                for n in range(self.N):
                    product ^= self.__finite_field_mul(mix_matrix[row][n], temp_state_matrix[n][col])
                state[row][col] = product

    def __finite_field_mul(self, mul_l, mul_r) -> int:
        result = 0
        for _ in range(mul_l.bit_length()):
            if mul_l&0x01:
                result ^= mul_r
            mul_l >>= 1

            if mul_r & 0x80:
                mul_r <<= 1
                mul_r ^= 0x1B
            else:
                mul_r <<= 1
        return result&0xFF

    def __inv_sub_bytes(self, state):
        for row in range(self.N):
            for col in range(self.N):
                state[row][col] = self.__l_sbox[state[row][col]>>4][state[row][col]&0x0F]
        

    def __inv_shift_rows(self, state):
        shift_num = 3
        for row in range(1, self.N):
            for _ in range(shift_num):
                byte = state[row][0]
                for n in range(self.N - 1):
                    state[row][n] = state[row][n+1]
                state[row][3] = byte
            shift_num -= 1
        

    def __inv_mix_columns(self, state):
        inv_mix_matrix = [[0x0E, 0x0B, 0x0D, 0x09],
                          [0x09, 0x0E, 0x0B, 0x0D],
                          [0x0D, 0x09, 0x0E, 0x0B],
                          [0x0B, 0x0D, 0x09, 0x0E]]
        temp_state_matrix = copy.deepcopy(state)
        for row in range(self.N):
            for col in range(self.N):
                product = 0
                for n in range(self.N):
                    product ^= self.__finite_field_mul(inv_mix_matrix[row][n], temp_state_matrix[n][col])
                state[row][col] = product
    
    def __T(self, W, rounds) -> int:
        sub_word_list = []
        # shift one byte
        W = ((W<<8)|(W>>24))&0xFFFFFFFF
        # sub word
        bytes_array = W.to_bytes(4, byteorder='big', signed=False)
        for byte in bytes_array:
            sub_word_list.append(self.__s_box[byte>>4][byte&0x0F])
        W = int.from_bytes(bytes(sub_word_list), byteorder='big', signed=False)  
        # xor rcon
        W ^= self.__Rcon[rounds//4 - 1]
        return W

    def __key_extension(self, key) -> list:
        W = [int.from_bytes(key[i*4:i*4+4], byteorder='big', signed = False) for i in range(self.N)]
        key_state_matrix = [[] for _ in range(11)]
        for rounds in range(4, 44):
            if rounds%4 != 0:
                W.append(W[rounds - 4] ^ W[rounds - 1])
            else:
                W.append(W[rounds - 4] ^ self.__T(W[rounds - 1], rounds))
        
        for i in range(11):
            key_bytes = b''
            for n in range(self.N):
                key_bytes += W[i*4+n].to_bytes(4, byteorder='big', signed=False)
            key_state_matrix[i] = self.__to_state_matrix(key_bytes)
            
        return key_state_matrix
    
    def __to_state_matrix(self, msg) -> list:
        state = [[] for _ in range(self.N)]
        for row in range(self.N):
            for col in range(self.N):
                state[row].append(msg[col*4+row])
        return state

    def __to_bytes(self, state) -> bytes:
        msg_bytes = b''
        for row in range(self.N):
            for col in range(self.N):
                msg_bytes += bytes([state[col][row]])
        return msg_bytes

    def __aes_encrypt(self, plain) -> bytes:
        self.__msg_state_matrix = self.__to_state_matrix(plain)
        self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[0])
        for rounds in range(1, 10):
            self.__sub_bytes(self.__msg_state_matrix)
            self.__shift_rows(self.__msg_state_matrix)
            self.__mix_columns(self.__msg_state_matrix)
            self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[rounds])
        self.__sub_bytes(self.__msg_state_matrix)
        self.__shift_rows(self.__msg_state_matrix)
        self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[10])
        cipher = self.__to_bytes(self.__msg_state_matrix)
        return cipher

    def __aes_decrypt(self, cipher) -> bytes:
        self.__msg_state_matrix = self.__to_state_matrix(cipher)
        self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[10])
        for rounds in range(9, 0, -1):
            self.__inv_shift_rows(self.__msg_state_matrix)
            self.__inv_sub_bytes(self.__msg_state_matrix)
            self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[rounds])
            self.__inv_mix_columns(self.__msg_state_matrix)
        self.__inv_shift_rows(self.__msg_state_matrix)
        self.__inv_sub_bytes(self.__msg_state_matrix)
        self.__add_round_key(self.__msg_state_matrix, self.__key_state_matrix[0])
        plain = self.__to_bytes(self.__msg_state_matrix)
        return plain

    def __msg_group(self, msg) -> list:
        PADDING_DATA = b'\x00'
        msg_group = []
        msg_length = len(msg)
        if msg_length%16 == 0:
            group_num = msg_length // 16
        else:
            padding_length = 16 - msg_length%16
            msg+= padding_length*PADDING_DATA
            group_num = msg_length // 16 + 1
        
        for i in range(group_num):
            msg_group.append(msg[i*16:i*16+16])

        return msg_group

    def set_key(self, key):
        self.__key = key
        self.__key_state_matrix = self.__key_extension(self.__key)
        

    def encrypt(self, plain) -> bytes:
        msg_group_list = self.__msg_group(plain)
        cipher = b''
        for msg in msg_group_list:
            cipher += self.__aes_encrypt(msg)
        
        return cipher

    def decrypt(self, cipher):
        msg_group_list = self.__msg_group(cipher)
        plain = b''
        for msg in msg_group_list:
            plain += self.__aes_decrypt(msg)

        return plain
    
    def __str__(self) -> str:
        def print_matrix(state):
            rounds = 0
            for matrix in state:
                for i in matrix:
                    print(list(map(hex,i)))
                print('')
                
        key = self.__key
        print('key is %s' % key)
        print_matrix(self.__key_state_matrix)
    def test_func(self):
        def print_matrix(state):
            for i in state: 
                print(list(map(hex,i)))
            print('')
        
if __name__ == "__main__":
    # 2b7e151628aed2a6abf7158809cf4f3c
    # 3243f6a8885a308d313198a2e0370734
    plain = b'aaaabbbbccccddddabcd'
    aes = AES(b'+~\x15\x16(\xae\xd2\xa6\xab\xf7\x15\x88\t\xcfO<')
    cipher = aes.encrypt(plain)
    print(cipher)
    print(aes.decrypt(cipher))
    