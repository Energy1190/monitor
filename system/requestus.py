import sys
import datetime
from traceback import format_exc
from classes.db_mongo import Database

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

def get_route_info_database(*args, start_time=None, end_time=None, deep=4, output=sys.stdout, error=sys.stderr, **kvargs):
    """
    Обращается к базе данных по предоставленному фильтру. Обрабатывает и суммирует
    полученный результат.
    :param args:
    :param start_time:
    :param end_time:
    :param deep:
    :param kvargs:
    :return:
    """
    def remove_temp(x):
        """
        Удаляет ненужные значения из словаря
        :return:
        """
        removable = ['start_time', 'end_time', 'deep', 'limited', 'output', 'error']
        for i in x:
            if i in removable:
                del x[i]
        return x

    def get_time_tuple(time_str):
        """
        Приведение времени к datetime
        :param time_str:
        :return:
        """
        if time_str:
            try:
                return datetime.datetime(*tuple(map(lambda x: int(x), time_str.split(sep='_'))))
            except:
                try:
                    return datetime.datetime(*time_str)
                except:
                    return (datetime.datetime.now() + datetime.timedelta(hours=3))
        else:
            return False

    def get_target(start_time, end_time):
        if start_time.timetuple()[2] != end_time.timetuple()[2]:
            ee = end_time.timetuple()
            ss = start_time.timetuple()
            target = [['route', 'base-{0}-{1}-{2}'.format(j,h,i)] for i in range(ss[2],ee[2]+1)
                      for h in range(ss[1],ee[1]+1)
                      for j in range(ss[0],ee[0]+1)]
        elif start_time.timetuple()[0:2] == datetime.datetime.now().timetuple()[0:2]:
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            target = ['route', target_collection]
        else:
            ss = start_time.timetuple()
            target = ['route', 'base-{0}-{1}-{2}'.format(ss[0],ss[1],ss[2])]
        return target

    def get_time_requests(start_time, end_time, deep=4):
        try:
            r = []
            x = start_time.timetuple()[0:deep]
            y = end_time.timetuple()[0:deep]
            while x != y:
                if x not in r:
                    r.append(x)
                start_time = start_time + datetime.timedelta(minutes=1)
                x = start_time.timetuple()[0:deep]
            r.append(x)
            return r
        except Exception as err:
            pass

    def get_answer(dx, target, visibal=False, output=None):
        if visibal:
            limit = 100
        else:
            limit = 1000000
        x = []
        y = []
        if type(target[0]) == list:
            for j in target:
                y += Database(dicts=dx, target=j, limit=limit).find()
        else:
            y = Database(dicts=dx, target=target, limit=limit).find()
        for i in y:
            del i['_id']
            if i not in x:
                x.append(i)
        print('Object {0} contains {1} items'.format(str(dx), str(len(x))), file=output)
        return x

    def detect_var(target, time, output=None):
        if type(target) == list:
            target = target[0]
        x = int(time[0][0])
        y = str(time[0][0])
        d = Database(target=target)
        d.change(dicts={'year': x})
        if d.count(d.find):
            return int
        d.change(dicts={'year': y})
        if d.count(d.find):
            return str
        return False

    try:
        print('Start generating a query to the database', file=output)
        x = []
        limited = kvargs.get('limited')         # Флаг лимитирующий результаты запросов.
        dx = remove_temp(kvargs)                # Фильтер для поиска в базе.
        start_time = get_time_tuple(start_time or
                                     kvargs.get('start_time') or
                                     ((datetime.datetime.now() + datetime.timedelta(hours=3)) - datetime.timedelta(days=1)))
        end_time = get_time_tuple((end_time or
                                   kvargs.get('end_time') or
                                   (datetime.datetime.now() + datetime.timedelta(hours=3))))
        target = get_target(start_time, end_time)
        t = get_time_requests(start_time, end_time, deep=deep)
        print('All parameters were successfully received', file=output)
        print('Filter for request: {0}'.format(str(dx)), file=output)
        print('Collection(s) of destination: {0}'.format(str(target)), file=output)
        print('Time Filter: {0}'.format(str(t)), file=output)
        typeus = detect_var(target, t)
        if t and typeus:
            for j in t:
                if len(j) >= 1:
                    dx['year'] = typeus(j[0])
                if len(j) >= 2:
                    dx['month'] = typeus(j[1])
                if len(j) >= 3:
                    dx['day'] = typeus(j[2])
                if len(j) >= 4:
                    dx['hour'] = typeus(j[3])
                if len(j) >= 5:
                    dx['minute'] = typeus(j[4])
                for i in get_answer(dx, target, visibal=limited, output=output):
                    x.append(i)
            print('Request successfully processed, returned {0} items'.format(str(len(x))), file=output)
            return x
        else:
            print('No data matched the query or an error occurred with the type of variables')
            return x
    except:
        print('An error occurred while processing the request', file=error)
        print(format_exc(), file=error)
