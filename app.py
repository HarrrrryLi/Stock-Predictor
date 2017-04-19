#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import mysql.connector   #using mysql connector should install it first(python 2.7/3.3/3.4)
except ImportError:
    print('Please Install MySQL Connector(Python) First.')
    raise SystemExit()
try:
    from yahoo_finance import Share
except ImportError:
    import pip
    pip.main(['install', 'yahoo_finance'])
    from yahoo_finance import Share

try:
    import pandas as pd
    from pandas import DataFrame
except ImportError:
    import pip
    pip.main(['install', 'pandas'])
    import pandas as pd

try:
    import pandas_datareader as pdr
    from pandas_datareader import data, wb
except ImportError:
    import pip
    pip.main(['install', 'pandas_datareader'])
    import pandas_datareader as pdr
    from pandas_datareader import data, wb

try:
    from sqlalchemy import create_engine
except ImportError:
    import pip
    pip.main(['install', 'sqlalchemy'])
    from sqlalchemy import create_engine


try:
    from datetime import *
except ImportError:
    import pip
    pip.main(['install','datetime'])
    from datetime import *
    
import time
import base64
import random
import hmac
import time
import json
import os
import codecs
import StringIO
try:
    from flask import Flask, request, redirect, make_response,render_template
except ImportError:
    import pip
    pip.main(['install', 'flask'])
    from flask import Flask, request, redirect, make_response,render_template

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import matplotlib.pyplot as plt
except ImportError:
    import pip
    pip.main(['install','matplotlib'])
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import matplotlib.pyplot as plt


PassWord='password'
User='root'
Host='127.0.0.1'
Port='3306'
Database='SEProject'

try:
    cnx = mysql.connector.connect(user=User, password=PassWord,host=Host) #using configuration of sever
except mysql.connector.Error:
    print('Can Not Connect With Database Sever.')
    raise SystemExit()

cursor=cnx.cursor()
#using mysql to create real time data
create_Login_info='''CREATE TABLE IF NOT EXISTS login_info               
                       (
                          `user_name` CHAR(20),
                          `password` CHAR(20),
                          `email` CHAR(20),
                          PRIMARY KEY(user_name)
                         );'''
cursor.execute('CREATE DATABASE IF NOT EXISTS '+Database)  #creat database if not exists
cursor.execute('USE '+Database)  #select the database
cursor.execute(create_Login_info)  #create table

app = Flask(__name__)


login_uri = 'http://127.0.0.1:5000/client/passport'
register_uri = 'http://127.0.0.1:5000/register'
user = ' '
auth_code = {}    # use a dict to store authorization code
oauth_redirect_uri = []

TIME_OUT = 3600 * 2

def find_p(user_name):
    find_password='''SELECT login_info.password
                     FROM login_info
                     WHERE EXISTS(SELECT *
                                  WHERE login_info.user_name=\''''+user_name+'\');'
    cursor.execute(find_password)
    p=cursor.fetchall()
    return p

def find_e(email):
    find_email='''SELECT *
                  FROM login_info
                  WHERE login_info.email=\''''+email+'\';'
    cursor.execute(find_email)
    e=cursor.fetchall()
    return e



def gen_token(data):   # generalize token

    '''
    
    :param data: dict type
    :return: base64 str
    '''

    data = data.copy()

    if "salt" not in data:
        data["salt"] = unicode(random.random()).decode("ascii")
    if "expires" not in data:
        data["expires"] = time.time() + TIME_OUT

    payload = json.dumps(data).encode("utf-8")  # dict to json str

    # generalize signature
    sig = _get_signature(payload)   # generalize 16-bit string
    return encode_token_bytes(payload + sig) # json str + signature = new token  32-bit str


# this function is to generalize authorization code which in this case is just a random number
def gen_auth_code(uri, user_id):   # when verify code, uri is needed as well
    code = random.randint(0, 10000)
    auth_code[code] = [uri, user_id]
    return code   # authorization code


def verify_token(token):  # verify token
    '''
    
    :param token: base64 str
    :return: dict type
    '''
    decode_token = decode_token_bytes(str(token))  # base64 after decode
    payload = decode_token[:-16]   # start to 16th last element (uid+random+time) json string
    sig = decode_token[-16:]       # 16th last to the end (sig)

    # generalize signature
    expected_sig = _get_signature(payload)
    if sig != expected_sig:
        return {}
    data = json.loads(payload.decode("utf-8"))   # if token is correct, json str to dict
    if data.get("expires") >= time.time():  # if token not expired
        return data
    return 0


def _get_signature(value):  # HMAC ALGORITHM
    """Calculate the HMAC signature for the given value(any string)."""
    return hmac.new('secret123456', value).digest()


def encode_token_bytes(data):
    return base64.urlsafe_b64encode(data)


def decode_token_bytes(data):
    return base64.urlsafe_b64decode(data)


# verification-server-side:
@app.route('/index', methods=['POST', 'GET'])
def index():
    # print request.headers # print acquired headers to console
    print(request.headers)
    return "Hello"


# verify user's username and password correct or not,if correct return user a token
@app.route('/login', methods=['POST', 'GET'])
def login():
    # request's header to store user's uid and pw
    uid, pw = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).split(':')
    if find_p(uid) and find_p(uid)[0][0].encode("ascii") == pw:
        return gen_token(dict(user=uid, pw=pw))
    else:
        return redirect(login_uri);


# this function is to handle all the stuff with login verification
# it needs to check if the authorization code and uri redirection are correct or not
# if all the requirements match, then release the token
@app.route('/oauth', methods=['POST', 'GET'])
def oauth():
    # handle form login, and set Cookie meanwhile
    if request.method == 'POST' and request.form['username']:
        if request.args.get('redirect_uri')==login_uri:
            u = request.form['username']
            p = request.form['password']
            if find_p(u) and find_p(u)[0][0].encode("ascii") == p and oauth_redirect_uri:
                expire_date = datetime.utcnow() + timedelta(minutes=10)
                uri = oauth_redirect_uri[0] + '?code=%s' % gen_auth_code(oauth_redirect_uri[0], u)
                resp = make_response(redirect(uri))
                resp.set_cookie('login', '_'.join([u, p]), expires=expire_date)
                user=u
                return resp
            else:
                
                return  render_template("login.html",alert='Invalid Username or Password!')
        elif request.args.get('redirect_uri')==register_uri:
            u = request.form['username']
            p1 = request.form['password1']
            p2 = request.form['password2']
            email=request.form['E-mail']
            if not find_p(u):
                if not find_e(email):
                    if p1==p2:
                        cursor.execute('INSERT INTO login_info (user_name,password,email) VALUES (%s, %s,%s);',(u,p1,email))
                        cnx.commit()
                        resp = make_response(redirect('http://127.0.0.1:5000/client/login'))
                        resp.set_cookie('login', expires=0)
                        return resp
                    else:
                        return render_template("register.html",alert='Passwords are Differents!')
                else:
                    return render_template("register.html",alert='The Email has already been Registered')
            else:
                return render_template("register.html",alert='The Username has already been Used')
    # verify authorization code and release token
    if request.args.get('code'):
        auth_info = auth_code.get(int(request.args.get('code')))     # code = redirect_uri + user
        if auth_info[0] == request.args.get('redirect_uri'):
            # store user in auth_code of authorization code and package it in the token
            target1 = 'http://127.0.0.1:5000/logined?token=%s' %gen_token(dict(user=request.args.get('user'), user_id=auth_info[1]))
            return redirect(target1)    # gen_token(dict(user=request.args.get('user'), user_id=auth_info[1]))

    # if current login user has Cookie, skip verification, otherwise fill the form
    if request.args.get('redirect_uri'):
        oauth_redirect_uri.append(request.args.get('redirect_uri'))
        if request.args.get('redirect_uri')==register_uri:
            return render_template("register.html")
        elif request.args.get('redirect_uri')==login_uri:
            if request.cookies.get('login'):
                u, p = request.cookies.get('login').split('_')
                if find_p(u) and find_p(u)[0][0].encode("ascii") == p:
                    uri = oauth_redirect_uri[0] + '?code=%s' % gen_auth_code(oauth_redirect_uri[0], u)
                    return redirect(uri)
                else:
                    return redirect(login_uri)
            return render_template("login.html")

    # if request.args.get('redirect_uri'):
    #     oauth_redirect_uri.append(request.args.get('redirect_uri'))
    # if request.args.get('username'):
    #     if users.get(request.args.get('username'))[0] == request.args.get('password') and oauth_redirect_uri:  # user offers pw
    #         uri = oauth_redirect_uri[0] + '?code=%s' % gen_auth_code(oauth_redirect_uri[0])  # if pw, offer auth_code
    #         return redirect(uri)   # this redirect is to check the code see in next if
    # if request.args.get('code'):    # to check the request has auth code and earlier offered redirect_uri or not
    #     if auth_code.get(int(request.args.get('code'))) == request.args.get('redirect_uri'):
    #         return gen_token(request.args.get('user'))  # if no problem, give client the token
    # return 'please login'


# client-side:
# this function is to redirect all the requests sent to /client/login to http://localhost:5000/oauth
@app.route('/client/login', methods=['POST', 'GET'])
def client_login():
    uri = 'http://127.0.0.1:5000/oauth?response_type=code&user=%s&redirect_uri=%s' % (user, login_uri)
    return redirect(uri)


@app.route('/client/passport', methods=['POST', 'GET'])
def client_passport():
    code = request.args.get('code')
    uri = 'http://127.0.0.1:5000/oauth?grant_type=authorization_code&code=%s&redirect_uri=%s&user=%s' \
          % (code, login_uri, user)
    return redirect(uri)

@app.route('/client/register', methods=['POST', 'GET'])
def client_register():
    uri = 'http://127.0.0.1:5000/oauth?response_type=code&user=%s&redirect_uri=%s' % (user, register_uri)
    return redirect(uri)

@app.route('/home',methods=['POST','GET'])
def home():
    if request.method == 'POST'and request.form['stock']:
        stock=request.form['stock']
        uri='http://127.0.0.1:5000/stock?stock_name=%s'% stock
        return redirect(uri) 
    if request.cookies.get('login'):
        u, p = request.cookies.get('login').split('_')
        if find_p(u) and find_p(u)[0][0].encode("ascii") == p:
            '<head><style id="jsbin-css">.login{display:none;} .logout{display:inline}'
            return render_template('home.html',change='change')
    return render_template('home.html')

@app.route('/stock',methods=['POST','GET'])
def stock():
    return render_template("stockselect.html")
@app.route('/figure.png')
def figure():
    fig=Figure()
    ax=fig.add_subplot(111)
    x=range(100)
    y=range(100)
    ax.plot(x,y)
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/logout',methods=['POST','GET'])
def logout():
    resp = make_response(redirect('http://127.0.0.1:5000/home'))
    resp.set_cookie('login', expires=0)
    return resp


@app.route('/',methods=['POST','GET'])
def default():
	return redirect('http://127.0.0.1:5000/home')

# resource-server-side:
@app.route('/logined', methods=['POST', 'GET'])
def logined():
    token = request.args.get('token')
    ret = verify_token(token)
    if ret:
        return redirect('http://127.0.0.1:5000/home')
    else:
        resp = make_response(redirect('http://127.0.0.1:5000/home'))
        resp.set_cookie('login', expires=0)
        return redirect('http://127.0.0.1:5000/home')
if __name__ == '__main__':
    app.run(debug=True)
