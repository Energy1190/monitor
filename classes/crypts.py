import json
import base64
from Crypto import Random
from Crypto.Cipher import AES

class Crypt():
    def __init__(self):
        self.key = None

    def set_key(self, key):
        self.key = base64.b64decode(key)

    def remove_end(self, x):
        """
        Входящие сообщения имеют стандартные окончания файлов вида "\r \n"
        При дешифрофке эти символы мешают преобразовать полученную строку в
        словарь. Предполагается, что этих символов будет не больше 100, метод
        отбрасывает ненужные символы последовательно, пока не сможет преобразовать
        строку в словарь. Возвращает расшифрованные данные.
        :param x:
        :return:
        """
        for i in range(100):
            try:
                return json.loads(str(self.decrypt(x)[:-i], 'utf-8'))
            except:
                pass
        return False

    def encrypt(self, raw):
        """
        Метод шифрования объектов в AES.
        :param raw:
        :return:
        """
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt(self, enc):
        """
        Метод дешифрования объектов из AES. Требует значение self.key
        :param enc:
        :return:
        """
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return cipher.decrypt( enc[16:] )