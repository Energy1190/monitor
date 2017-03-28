#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from classes.db_mongo import Database
from classes.clients import Base

def delete_old_reqests(target, status='Old'):
    """Процедура очистки устаревших/обработанных объектов в базе данных,
    так же реализована возможность полного удаления коллекции базы данных,
    при отсутствии именованного аргумента status.
    """
    try:
        if status:
            trg = Database(target=target, fild='Status', fild_var=status).get()
            for i in trg:
                Database(dicts=i, target=target).delete()
        else:
            Database(target=target).delete_all()
    except:
        pass

def check_base(target):
    """Процедура проверки коллекции базы данных. На данный момент реализована
    только проверка коллекций users, copms и dhcp. Ищет и удаляет пустые, не имеющие имени,
    объекты из базы данных. Проверка осуществляется по одному ключу-значению в словаре
    назначения. Предполагается, что объект не может быть правильным без этого значения.
    Проверка осуществляется в нижнем регистре, чтобы измежать появления объектов копий.

    Функция в зависимости от переданного ей аргумента, целевой базы коллекции данных,
    определяет ключ для проверки сроваря. Если переданный аргумент не соответствует
    ожиданиям функция вернет False. Аргумент должен быть итерабельным, как минимум из
    двух элементов, в противном случае функция завершится с ошибкой.

    После определения ключа для каждого элемента в коллекции идет его проверка на
    не нулевое значение, а затем на соответствие с полученными ранее значениям (для dhcp включена
    проверка на время получения значения, будет сохраняться более новое значение), если
    проверка пройдена проверяемый объект словаря добавляется в список y и будет участвовать
    в последующих проверках, если хотя бы одна проверка не была пройдена проверяемый
    элемент удаляется из коллекции.
    """
    y = []
    x = Database(target=target, limit=10000).find()
    if target[1] == 'comps':
        name = 'computername'
    elif target[1] == 'users':
        name = 'username'
    elif target[1] == 'dhcp':
        name = 'ip'
        y = {}
    else:
        return False
    for i in x:
        for j in i:
            if j == name:
                if i[j]:
                    if i[j].lower() not in y and name != 'ip':
                        y.append(i[j].lower())
                        break
                    elif name == 'ip' and str(i[j]).lower() not in list(y):
                        if y.get(str(i[j]).lower()) and i['time'] < y.get(str(i[j]).lower()):
                            print('delete:', i)
                            Database(dicts=i, target=target).delete()
                        else:
                            y[str(i[j]).lower()] = i['time']
                    else:
                        print('delete:', i)
                        Database(dicts=i, target=target).delete()
                else:
                    print('delete:', i)
                    Database(dicts=i, target=target).delete()
        if name not in i:
            Database(dicts=i, target=target).delete()

def get_database_incoming(target, status=None):
    if status:
        return Database(target=target, fild='Status', fild_var=status).get()
    else:
        return Database(target=target).get()

def decrypt_str(t):
    d = t.get('Targets')
    return [Base(t).remove_end(t.get('Body')), d]

if __name__ == '__main__':
    pass