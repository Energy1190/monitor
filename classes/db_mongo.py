import pymongo
from bson.objectid import ObjectId

class Database():
    def __init__(self, target=None, dicts=None, fild=None, fild_var=None, id=None, limit=100000,
                client=('mongoDB', 27017)):
        self.db = pymongo.MongoClient(*client)
        self.target = target
        self.path = self._db_path(self.target)
        self.dicts=dicts
        self.fild=fild
        self.fild_var=fild_var
        self.id = self._id_test(id)
        self.limit = limit
        if self.fild and self.fild_var and not self.dicts:
            self.dicts = {self.fild: self.fild_var}
        elif self.id and not self.dicts:
            self.dicts = {'_id': self.id}
        if dicts and '_id' in dicts:
            del self.dicts['_id']

    def _db_path(self, target=None):
        if target:
            if len(target) == 1:
                return self.db[target[0]]
            elif len(target) == 2:
                return self.db[target[0]][target[1]]

    def _id_test(self, num):
        if num:
            try:
                return ObjectId(num)
            except:
                return ObjectId(str(num))

    def set(self, x, path=None):
        if path:
            return self._db_path(target=path).save(x)
        else:
            return self.path.save(x)

    def get(self):
        if self.dicts:
            return self.path.find_one(self.dicts)
        else:
            return self.path.find_one()

    def find(self):
        if self.dicts:
            return self.path.find(self.dicts, limit=self.limit)
        else:
            return self.path.find(limit=self.limit)

    def delete(self):
        return self.path.delete_one(self.dicts)

    def delete_all(self):
        return self.path.delete_many()

    def update(self, x, path=None):
        if path:
            return self._db_path(target=path).replace_one(self.dicts, x)
        else:
            return self.path.replace_one(self.dicts, x)