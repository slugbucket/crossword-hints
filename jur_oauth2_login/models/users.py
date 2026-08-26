# -*- coding: utf-8 -*-
"""
Users model for LDAP auth
"""
from datetime import datetime
import sqlite3
from peewee import Model, AutoField, CharField, DateTimeField, SqliteDatabase
from crossword_hints import application

__all__ = ["database"]


database = SqliteDatabase(
    application.config["DATABASE"], pragmas=(("foreign_keys", "on"),)
)
database.row_factory = sqlite3.Row


class BaseModel(Model):
    """
     D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G
                                                           
        A base model that will use our Sqlite database.
        Appears to be incompatible with Flask TestCase
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


class Users(BaseModel):
    """
    Users model class
    """
    rowid = AutoField()
    username = CharField(null=False, max_length=32, unique=True)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())


    @staticmethod
    def is_authenticated(self):
        """"
        Confirm authenticated user
        """
        return True


    def is_active(self):
        """
        Confirm active user
        """
        return True


    def is_anonymous(self):
        """
        No anonymous users
        """
        return False


    def get_id(self):
        """
        Return userid
        """
        return self.rowid


    def get_name(self):
        """
        Return username
        """
        return self

    # def current_user(self):
    #     """
    #     Return current user
    #     """
    #     # return self.username
    #     return "julian"
