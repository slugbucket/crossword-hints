# -*- coding: utf-8 -*-
"""
Crossword hints database model
"""

from datetime import datetime
import sqlite3
from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    IntegerField,
    TextField,
    ForeignKeyField,
    Model,
)
from crossword_hints import application

__all__ = ["database", "init_db"]


database = sqlite3.SqliteDatabase(
    application.config["DATABASE"], pragmas=(("foreign_keys", "on"),)
)
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
    """
    Database initialiser
    """
    database.create_tables(
        [
            setter_types,
            crossword_setters,
            solution_types,
            crossword_solutions,
            activity_logs,
            cue_words,
            users,
        ]
    )


class BaseModel(Model):
    """
    D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G

    """

    with application.app_context():

        class Meta:
            """
            A base model that will use our Sqlite database.
            Appears to be incompatible with Flask TestCase
            """

            database = database

        def __str__(self):
            return f"{self.__class__.__name__}"


class activity_logs(BaseModel):
    """
    Activity log model
    """

    rowid = AutoField()
    actor = CharField(max_length=32)
    action = CharField(max_length=32)
    item_type = CharField(max_length=32)
    item_id = IntegerField()
    act_action = TextField()
    created_at = CharField(max_length=32)
    updated_at = DateTimeField(default=datetime.now())


class setter_types(BaseModel):
    """
    Setter types model
    """

    rowid = AutoField()
    name = CharField(null=False, max_length=16, unique=True)
    description = TextField()
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


class crossword_setters(BaseModel):
    """
    Crossword setters model
    """

    rowid = AutoField()
    name = CharField(null=False, unique=True, max_length=32)
    setter_type = ForeignKeyField(setter_types)
    description = TextField()
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


class solution_types(BaseModel):
    """
    Solution types model
    """

    rowid = AutoField()
    name = CharField(null=False, unique=True, max_length=32)
    description = TextField()
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


class crossword_solutions(BaseModel):
    """
    Crossword solutions model
    """

    rowid = AutoField()
    crossword_setter = ForeignKeyField(crossword_setters)
    clue = CharField(null=False, max_length=96)
    solution = CharField(null=False, max_length=128)
    solution_hint = CharField(null=False, max_length=128)
    solution_type = ForeignKeyField(solution_types)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


class cue_words(BaseModel):
    """
    Cue words model
    """

    rowid = AutoField()
    cue_word = CharField(null=False, max_length=32)
    meaning = CharField(null=False, max_length=128)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


class users(BaseModel):
    """
    Users model
    """

    rowid = AutoField()
    username = CharField(null=False, max_length=32, unique=True)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


#
#    E N D   O F   D A T A B A S E   M O D E L
#
