'''
    Очищает от повторений список compslist для всех пользователей
'''

from classes.db_mongo import Database

def main():
    t = Database(target=['clients','users']).find()
    if t:
        for i in list(t):
            x = []
            del i['_id']
            for j in i['compslist']:
                if j not in x:
                    x.append(j)
                else:
                    print('Duplicate {0} in user {1}'.format(str(j), str(i['username'])))
            i['compslist'] = x
            Database(target=['clients','users'], fild='username', fild_var=i['username']).update(i)