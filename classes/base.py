import json
import time
import base64
import datetime
from Crypto.Cipher import AES
from Crypto import Random
from classes.db_mongo import Database

class Base():
    """ Базовый класс для обработки входящих JSON-объектов. Включает в себя необходимые объекты:

    * old - список со значениями, которые были заменены в результате обновления записи в
    базе данных.
    * dicts - словарь, который будет по умолчанию записан в базу данных.
    * dst - коллекйия в базе данных, куда будет производиться запись, а так же откуда будут
    извлекаться значения для проверки по умолчанию.
    """
    def __init__(self, trg, target=None):
        self.old = []
        self.dicts = {}
        self.dst = target
        self.key = None
        self.body = None
        self.db = Database(target=target, dicts=trg)
        if type(trg) == dict:
            if trg.get('Key'):
                self.key = base64.b64decode(trg['Key'])
            if trg.get('Body'):
                self.body = trg['Body']

    def remove_end(self, x):
        for i in range(100):
            try:
                return json.loads(str(self.decrypt(x)[:-i], 'utf-8'))
            except:
                pass
        return False

    def encrypt( self, raw ):
        """
        Метод шифрования объектов в AES.
        :param raw:
        :return:
        """
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        """
        Метод дешифрования объектов из AES. Требует значение self.key
        :param enc:
        :return:
        """
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return cipher.decrypt( enc[16:] )

    def get_time_dict(self):
        """
        Метод для записи в словарь информации о времени. Разбитие времени на отдельные
        элементы сделано для более удобного поиска по базе данных
        :return:
        """
        if 'time' in self.__dict__:
            if type(self.time) == time.struct_time:
                self.dicts['time'] = time.strftime('%d.%m.%Y %H:%M:%S', self.time)
                self.time = datetime.datetime.fromtimestamp(time.mktime(self.time))
            else:
                self.dicts['time'] = self.time
            self.dicts['year'] = self.time.year
            self.dicts['month'] = self.time.month
            self.dicts['day'] = self.time.day
            self.dicts['hour'] = self.time.hour
            self.dicts['min'] = self.time.minute
            self.dicts['second'] = self.time.second

    def set_dict(self):
        exeption = ['dicts', 'message', 'dst', 'Key', 'Body', 'Targets', 'Crypt', 'key', 'body']
        self.dicts = {i: self.__dict__[i] for i in self.__dict__ if i not in exeption}

    def delete(self, trg, target=None):
        if target:
            self.db.delete()

    def set(self, trg=None, target=None):
        if target:
            self.db.set(trg, path=target)
        elif trg:
            self.db.set(trg)
        else:
            self.db.set(self.dicts)

    def update(self, srctrg=None, dsttrg=None, target=None):
        if target and dsttrg:
            if srctrg:
                Database(target=target, dicts=dsttrg).update(srctrg)
            else:
                Database(target=target, dicts=dsttrg).update(self.dicts)
        elif dsttrg:
            if srctrg:
                Database(target=self.dst, dicts=dsttrg).update(srctrg)
            else:
                Database(target=self.dst, dicts=dsttrg).update(self.dicts)

    def check_dict(self, target_dict):
        """
        Метод для проверки идентичности словарей. Исключает
        значения _id (идентификационный номер записи в базе данных) и old
        (список со старыми значениями). В случае обнаружения различий в
        записях - записывает устаревшее значение в словарь old с указанием
        времени сделаных изменений.
        :param target_dict:
        :return:
        """
        for i in self.dicts:
            if i != '_id' and i != 'old' and i in target_dict:
                if self.dicts[i] != target_dict[i]:
                    self.old.append({i: target_dict[i], 'time': (datetime.datetime.now() + datetime.timedelta(hours=3))})

    def get_dsttrg(self, src, fild):
        """
        Метод для получения объекта из целевой базы данных. Ищет объект по элементу
        словаря ключ(fild) - значение(src)
        :param src:
        :param fild:
        :return:
        """
        x = Database(target=self.dst, fild=fild, fild_var=src).get()
        if x:
            return x
        else:
            return False
