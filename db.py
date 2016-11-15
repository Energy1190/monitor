import pymongo
from bson.objectid import ObjectId

def db_path(target=None):
    if target is None:
        target = ['database', 'forms']
    db = pymongo.MongoClient('mongoDB', 27017)
    if len(target) == 1:
        return db[target[0]]
    elif len(target) == 2:
        return db[target[0]][target[1]]

def db_set(dict_db, target=None):
    return db_path(target).save(dict_db)

def db_get(id, target=None, fild='_id'):
    if fild == '_id':
        id = ObjectId(id)
    return db_path(target).find_one({fild: id})

def db_update(dict_db, target=None, fild='_id', id=None):
    if '_id' in dict_db:
        del dict_db['_id']
    if fild == '_id':
        fild = {'_id': ObjectId(id)}
    return db_path(target).replace_one(fild, dict_db)

def db_find(target=None):
    return db_path(target).find()

if __name__ == "__main__":
    db = pymongo.MongoClient()
#    print(db_get('57aa00e220d9773d3005a235'))
#    print(db_get('open', target=['database', 'task'], fild='status'))
    for i in db['database']['task'].find():
        print(i)