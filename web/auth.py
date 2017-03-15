import ldap3
from functools import wraps
from configuration import get_val
from flask import request, Response, session

logins = [{'name': 'admin', 'pass': 'secret'}]

def get_ldap_info():
    x = get_val('[LDAP]')
    return [{'server': i['server'], 'domain': i['name']} for i in x]

def ldap_auth(username, password):
    server = ldap3.Server(get_ldap_info()[0]['server'])
    conn = ldap3.Connection(server, user=str(get_ldap_info()[0]['domain']+ '\\' + username), password=password, authentication=ldap3.NTLM)
    return bool(conn.bind())

def check_auth(username, password):
    for i in logins:
        if i['name'] == username:
            if i['pass'] == password:
                return True
    return ldap_auth(username, password)

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