import pymongo
from bson.objectid import ObjectId

def counter(class_name, operation):
    def class_count(func):
        def wraper(*args, **kwargs):
            x = Count()
            x.set_count(class_name, operation)
            return func(*args, **kwargs)
        return wraper()

class Database():
    @counter('Database', 'create')
    def __init__(self, target=None, dicts=None, fild=None, fild_var=None, id=None, limit=100000,
                client=('mongoDB', 27017)):
        self.db = pymongo.MongoClient(*client)
        self.target = target
        self.path = self._db_path(self.target)
        self.dicts= dicts
        self.fild=fild
        self.fild_var=fild_var
        self.id = self._id_test(id)
        self.limit = limit
        self._check_fild()
        self._del(self.dicts)
        if self.id and not self.dicts:
            self.dicts = {'_id': self.id}

    def __setattr__(self, key, value):
        if key == 'dicts' and value:
            value = dict(value)
        return object.__setattr__(self, key, value)

    def _db_path(self, target=None):
        if target:
            if len(target) == 1:
                return self.db[target[0]]
            elif len(target) == 2:
                return self.db[target[0]][target[1]]

    def _del(self, x):
        if x and '_id' in x:
            del x['_id']
        if x and 'db' in x:
            del x['db']
        return x

    def _id_test(self, num):
        if num:
            try:
                return ObjectId(num)
            except:
                return ObjectId(str(num))

    def _check_fild(self):
        if self.fild and self.fild_var and not self.dicts:
            self.dicts = {self.fild: self.fild_var}

    def change(self, **kvargs):
        for i in kvargs:
            if i in self.__dict__:
                self.__dict__[i] = kvargs[i]
        self._check_fild()
        self._del(self.dicts)

    @counter('Database', 'set')
    def set(self, x, path=None):
        x = self._del(dict(x))
        if x:
            if path:
                return self._db_path(target=path).save(x)
            else:
                return self.path.save(x)

    @counter('Database', 'get')
    def get(self):
        if self.dicts:
            return self.path.find_one(self.dicts)
        else:
            return self.path.find_one()

    @counter('Database', 'find')
    def find(self):
        if self.dicts:
            return self.path.find(self.dicts, limit=self.limit)
        else:
            return self.path.find(limit=self.limit)

    @counter('Database', 'delete')
    def delete(self):
        return self.path.delete_one(self.dicts)

    @counter('Database', 'full-delete')
    def delete_all(self):
        return self.path.delete_many()

    @counter('Database', 'update')
    def update(self, x, path=None):
        x = dict(x)
        if path:
            return self._db_path(target=path).replace_one(self.dicts, x)
        else:
            return self.path.replace_one(self.dicts, x)

    def count(self, func, *args, **kwargs):
        return (func(*args, **kwargs).count())

class Count():
    names = []
    base = []
    db = Database(target=['systems', 'counts'])

    def get_base(self):
        return list(self.db.find())

    def set_count(self, name, operant):
        self.name = name
        self.count = 1
        if name not in Count.names:
            Count.base.append(name)
            Count.base.append({'name': self.name, 'count': self.count})
            return {'name': self.name, 'count': self.count, 'operation': operant}
        else:
            for i in Count.base:
                if i and i['name'] == name:
                    if i['operation'] == operant:
                        i['count'] = i['count'] + self.count
                        return i

    def update_base(self):
        x = self.get_base()
        if x:
            for i in Count.base:
                self.db.change(dicts={'name': i['name'], 'operation': i['operation']})
                self.db.update(i)
        else:
            for i in Count.base:
                self.db.set(i)
        Count.names = []
        Count.base = []

