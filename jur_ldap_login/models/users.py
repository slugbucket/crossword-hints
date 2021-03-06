# -*- coding: utf-8 -*-
import sqlite3
from peewee import *
from datetime import date, timedelta, datetime
import ldap
from crossword_hints import application

__all__ = ["database"]


database = SqliteDatabase(application.config['DATABASE'], pragmas=(("foreign_keys", "on"),))
database.row_factory = sqlite3.Row

def get_ldap_connection():
    conn = ldap.initialize(application.config['LDAP_PROVIDER_URL'])
    return conn
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
"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """

class users(BaseModel):
    rowid            = AutoField()
    username         = CharField(null=False, max_length=32, unique=True)
    created_at       = DateTimeField(default=datetime.now())
    updated_at       = DateTimeField(default=datetime.now())

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
