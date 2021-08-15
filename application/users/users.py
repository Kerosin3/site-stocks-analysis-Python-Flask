from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import hashlib, uuid
import random

class User():

    def __init__(self,id,username,password):
        self.id = id
        self.username = username
        self.salt = str(uuid.uuid4())
        # print(type(self.salt))
        self.password = hashlib.sha512( (password + self.salt).encode('utf-8') ).hexdigest()
        self.__real_password = password


    def __repr__(self):
        return f'<User: {self.username}, with id = {self.id}'

users_list = []
users_list.append(User(id=1,username='Admin',password='admin'))
# print(users_list[0].username)
# print(users_list[0].password)
