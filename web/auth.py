from functools import wraps
from flask import request, Response

def check_auth(username, password):
    user = 'admin'
    pasw = 'secret'
    return username == user and password == pasw

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
        return func(*args, **kwargs)
    return decorator