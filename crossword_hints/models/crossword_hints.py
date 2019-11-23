# -*- coding: utf-8 -*-
import sqlite3
from peewee import *
from datetime import date, timedelta, datetime
from crossword_hints import application

__all__ = ["database", "init_db"]


database = SqliteDatabase(application.config['DATABASE'], pragmas=(("foreign_keys", "on"),))
database.row_factory = sqlite3.Row
"""
Initialise the database - only to be used for testing and database restore
To bootstrap a database, either empty or with new schema:
Params:
  None
Returns:
  None
"""
def init_db():
    database.create_tables([setter_types, crossword_setters, solution_types, crossword_solutions, activity_logs, cue_words, users])


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



"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """