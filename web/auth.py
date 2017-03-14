from functools import wraps
from flask import request, Response, session

logins = [{'name': 'admin', 'pass': 'secret'}]

def check_auth(username, password):
    for i in logins:
        if i['name'] == username:
            if i['pass'] == password:
                return True
    return False

def fail_auth():
    return Response('Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def auth(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        x = request.authorization
        if not x or not check_auth(x.username, x.password):
            return fail_auth()
        session['username'] = x.username
        return func(*args, **kwargs)
    return decorator