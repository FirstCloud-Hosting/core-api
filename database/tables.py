#!flask/bin/python
# -*- coding: utf-8 -*-

import uuid
import datetime

from peewee import *

DB = MySQLDatabase(None)  # Create a blank database here


class BaseModel(Model):
    class Meta:
        database = DB


class Types(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = CharField(max_length=20)
    icon = CharField(max_length=255)


class Modules(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    type = ForeignKeyField(Types)
    name = CharField(max_length=255)
    page = CharField(max_length=255)
    forAdmin = IntegerField(default=0)


class Organizations(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    validity = IntegerField(default=-1)
    passwordHardening = IntegerField(default=0)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Groups(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    organization = ForeignKeyField(Organizations)
    name = CharField(max_length=255)
    note = TextField()
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Permissions(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    module = ForeignKeyField(Modules)
    group = ForeignKeyField(Groups)
    view = IntegerField(default=1)
    creation = IntegerField(default=0)
    edition = IntegerField(default=0)
    deletion = IntegerField(default=0)


class Languages(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = CharField(max_length=20)
    code = CharField(max_length=10)


class Users(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    organization = ForeignKeyField(Organizations)
    group = ForeignKeyField(Groups)
    password = CharField(max_length=64)
    status = IntegerField(default=0)
    confirmKey = UUIDField(default=uuid.uuid4)
    forgotPasswordKey = UUIDField(null=True)
    email = CharField(max_length=320)
    language = ForeignKeyField(Languages)
    mfa = CharField(max_length=3, default='off')
    mfaKey = CharField(max_length=25, null=True)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    edited = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.edited = datetime.datetime.now()
        return super(Users, self).save(*args, **kwargs)


class AppKeys(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = ForeignKeyField(Users)
    secretKey = UUIDField(default=uuid.uuid4)
    description = TextField(default='New application key')
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        db_table = 'appKeys'


class Countries(BaseModel):
    code = CharField(max_length=2, unique=True, primary_key=True)
    name = CharField(max_length=44)


class ApiConfigurations(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = CharField(max_length=2500)
    value = CharField(max_length=2500, null=True)

    class Meta:
        db_table = 'apiConfigurations'


class ActivityLogs(BaseModel):
    id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    activity = CharField(max_length=2500)
    result = TextField(null=True)
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        db_table = 'activityLogs'
