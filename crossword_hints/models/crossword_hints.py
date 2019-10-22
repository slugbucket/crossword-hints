# -*- coding: utf-8 -*-
from peewee import *
from datetime import date, timedelta, datetime
__all__ = ["activity_logs", "setter_types", "crossword_setters", "solution_types", "crossword_solutions", "cue_words"]

from peewee import *
from crossword_hints import application
from crossword_hints import database

"""                                                        """
"""  D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G  """
"""                                                        """
"""                                                        """
"""     A base model that will use our Sqlite database.    """
"""     Appears to be incompatible with Flask TestCase     """
class BaseModel(Model):
    with application.app_context():
        class Meta:
            database = database

class activity_logs(BaseModel):
    rowid            = AutoField()
    actor            = CharField(max_length=32)
    action           = CharField(max_length=32)
    item_type        = CharField(max_length=32)
    item_id          = IntegerField()
    act_action       = TextField()
    created_at       = CharField(max_length=32)
    updated_at       = DateTimeField(default=datetime.now())

class setter_types(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, max_length=16, unique=True)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class crossword_setters(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, unique=True, max_length=32)
    setter_type      = ForeignKeyField(setter_types)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class solution_types(BaseModel):
    rowid            = AutoField()
    name             = CharField(null=False, unique=True, max_length=32)
    description      = TextField()
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class crossword_solutions(BaseModel):
    rowid            = AutoField()
    crossword_setter = ForeignKeyField(crossword_setters)
    clue             = CharField(null=False, max_length=96)
    solution         = CharField(null=False, max_length=128)
    solution_hint    = CharField(null=False, max_length=128)
    solution_type    = ForeignKeyField(solution_types)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class cue_words(BaseModel):
    rowid            = AutoField()
    cue_word         = CharField(null=False, max_length=32)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

class users(BaseModel):
    rowid            = AutoField()
    username         = CharField(null=False, max_length=32, unique=True)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

    #def __init__(self, username, password):
    #    self.username = username

    @staticmethod
    def try_login(username, password):
        conn = get_ldap_connection()
        conn.simple_bind_s(
            'uid=%s,ou=People,dc=my-domain,dc=com' % username, password
        )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return(self.rowid)

    def get_name(self):
        return(self.username)

"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """